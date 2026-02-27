"""
Agentic Orchestrator using LangGraph for workflow management.
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from uuid import UUID, uuid4
import asyncio
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.models import Workflow, WorkflowExecution
from app.database import get_db
from app.services.workflow_scheduler import get_scheduler
from app.services.workflow_definitions import get_workflow_template, list_workflow_templates


class WorkflowState(Dict[str, Any]):
    """State object for LangGraph workflows."""
    pass


class AgenticOrchestrator:
    """
    Orchestrates automated workflows using LangGraph.
    Supports sequential and parallel execution modes.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.memory = MemorySaver()
        self.active_workflows: Dict[str, StateGraph] = {}
        self.agents: Dict[str, Callable] = {}
        self.scheduler = get_scheduler()
        
    def register_agent(self, agent_type: str, agent_func: Callable):
        """Register an agent function for use in workflows."""
        self.agents[agent_type] = agent_func
    
    async def executeWorkflow(
        self,
        workflow_id: UUID,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow by ID.
        
        Args:
            workflow_id: UUID of the workflow to execute
            context: Optional context data to pass to the workflow
            
        Returns:
            Dictionary containing execution results
        """
        # Get workflow from database
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status="running",
            started_at=datetime.utcnow()
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        try:
            start_time = datetime.utcnow()
            
            # Build the graph from workflow definition
            graph = self._build_graph(workflow.definition, workflow.execution_mode)
            
            # Initialize state
            initial_state = {
                "workflow_id": str(workflow_id),
                "execution_id": str(execution.id),
                "context": context or {},
                "results": {},
                "errors": []
            }
            
            # Execute the workflow
            final_state = await self._execute_graph(graph, initial_state, execution)
            
            # Ensure final_state is valid
            if final_state is None:
                final_state = initial_state
                final_state["errors"] = ["Workflow execution returned no state"]
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = int((end_time - start_time).total_seconds() * 1000)
            
            # Update execution record
            execution.status = "completed" if not final_state.get("errors") else "failed"
            execution.results = final_state.get("results", {})
            execution.errors = final_state.get("errors", [])
            execution.execution_time = execution_time
            execution.progress = 100
            execution.completed_at = end_time
            self.db.commit()
            
            return {
                "workflowId": str(workflow_id),
                "executionId": str(execution.id),
                "status": execution.status,
                "results": execution.results,
                "errors": execution.errors,
                "executionTime": execution_time
            }
            
        except Exception as e:
            # Update execution record with error
            execution.status = "failed"
            execution.errors = [str(e)]
            execution.completed_at = datetime.utcnow()
            self.db.commit()
            raise
    
    def _build_graph(self, definition: Dict[str, Any], execution_mode: str) -> StateGraph:
        """
        Build a LangGraph StateGraph from workflow definition.
        
        Args:
            definition: Workflow definition with nodes and edges
            execution_mode: "sequential" or "parallel"
            
        Returns:
            Configured StateGraph
        """
        # Create StateGraph with dict as state type
        workflow = StateGraph(dict)
        
        nodes = definition.get("nodes", [])
        edges = definition.get("edges", [])
        
        # Add nodes
        for node in nodes:
            node_id = node["id"]
            node_type = node["type"]
            
            if node_type == "agent":
                agent_type = node.get("agent")
                if agent_type in self.agents:
                    workflow.add_node(node_id, self.agents[agent_type])
                else:
                    # Create a placeholder node that does nothing
                    workflow.add_node(node_id, lambda state: state)
            elif node_type == "tool":
                # Tool nodes would call specific tools
                workflow.add_node(node_id, lambda state: state)
            elif node_type == "condition":
                # Conditional nodes for branching (pass-through)
                workflow.add_node(node_id, lambda state: state)
        
        # Handle parallel execution mode
        if execution_mode == "parallel":
            # For parallel execution, we need to identify independent branches
            # Find entry and finish nodes
            entry_nodes = [n["id"] for n in nodes if n.get("is_entry")]
            finish_nodes = [n["id"] for n in nodes if n.get("is_finish")]
            
            # If we have a start node that fans out to multiple nodes
            if entry_nodes and len(entry_nodes) == 1:
                start_node = entry_nodes[0]
                workflow.set_entry_point(start_node)
                
                # Find all nodes that start_node connects to
                parallel_nodes = [e["to"] for e in edges if e["from"] == start_node]
                
                # Add edges from start to all parallel nodes
                for edge in edges:
                    workflow.add_edge(edge["from"], edge["to"])
                
                # Connect finish nodes to END
                for node in finish_nodes:
                    workflow.add_edge(node, END)
            else:
                # Fallback: add all edges as defined
                for edge in edges:
                    workflow.add_edge(edge["from"], edge["to"])
                
                # Set entry point
                if entry_nodes:
                    workflow.set_entry_point(entry_nodes[0])
                
                # Connect finish nodes to END
                for node in finish_nodes:
                    workflow.add_edge(node, END)
        else:
            # Sequential execution: connect nodes in order as defined
            for edge in edges:
                workflow.add_edge(edge["from"], edge["to"])
            
            # Set entry point
            entry_nodes = [n["id"] for n in nodes if n.get("is_entry")]
            if entry_nodes:
                workflow.set_entry_point(entry_nodes[0])
            
            # Set finish point
            finish_nodes = [n["id"] for n in nodes if n.get("is_finish")]
            for node in finish_nodes:
                workflow.add_edge(node, END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def _execute_graph(
        self,
        graph: StateGraph,
        initial_state: WorkflowState,
        execution: WorkflowExecution
    ) -> WorkflowState:
        """
        Execute a compiled graph and update execution progress.
        
        Args:
            graph: Compiled StateGraph
            initial_state: Initial workflow state
            execution: WorkflowExecution record to update
            
        Returns:
            Final workflow state
        """
        config = {"configurable": {"thread_id": str(execution.id)}}
        
        # Execute the graph
        # LangGraph's astream returns chunks as {node_name: state_after_node}
        final_state = initial_state
        try:
            async for chunk in graph.astream(initial_state, config):
                # Each chunk is a dict with node_name as key and updated state as value
                for node_name, state in chunk.items():
                    # The state returned is the full state after the node executed
                    if state is not None:
                        final_state = state
                    
                    # Update progress
                    execution.current_node = node_name
                    self.db.commit()
        except Exception as e:
            # If execution fails, ensure we have a valid state
            if final_state is None:
                final_state = initial_state
            final_state["errors"] = final_state.get("errors", []) + [str(e)]
        
        # Ensure final_state is never None
        if final_state is None:
            final_state = initial_state
            
        return final_state
    
    async def scheduleWorkflow(
        self,
        workflow_id: UUID,
        schedule: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule a recurring workflow using cron syntax.
        
        Args:
            workflow_id: UUID of the workflow to schedule
            schedule: Cron schedule string (e.g., "0 9 * * *" for daily at 9am)
            context: Optional context to pass to workflow execution
            
        Returns:
            Schedule ID (job ID)
        """
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Update workflow with schedule
        workflow.schedule = schedule
        workflow.is_active = True
        self.db.commit()
        
        # Create orchestrator factory for scheduler
        def orchestrator_factory(db: Session):
            orchestrator = AgenticOrchestrator(db)
            # Register agents
            orchestrator.register_agent("price_alert", self.agents.get("price_alert"))
            orchestrator.register_agent("research", self.agents.get("research"))
            orchestrator.register_agent("rebalancing", self.agents.get("rebalancing"))
            return orchestrator
        
        # Schedule with APScheduler
        job_id = self.scheduler.schedule_workflow(
            workflow_id=workflow_id,
            cron_schedule=schedule,
            orchestrator_factory=orchestrator_factory,
            context=context
        )
        
        return job_id
    
    async def cancelWorkflow(self, workflow_id: UUID) -> None:
        """
        Cancel a scheduled workflow.
        
        Args:
            workflow_id: UUID of the workflow to cancel
        """
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Deactivate in database
        workflow.is_active = False
        self.db.commit()
        
        # Cancel scheduled job
        self.scheduler.cancel_workflow(workflow_id)
    
    async def getWorkflowStatus(self, execution_id: UUID) -> Dict[str, Any]:
        """
        Get the status of a workflow execution.
        
        Args:
            execution_id: UUID of the execution
            
        Returns:
            Dictionary containing execution status
        """
        execution = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.id == execution_id
        ).first()
        
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        return {
            "workflowId": str(execution.workflow_id),
            "executionId": str(execution.id),
            "status": execution.status,
            "progress": execution.progress,
            "currentNode": execution.current_node,
            "results": execution.results,
            "errors": execution.errors,
            "executionTime": execution.execution_time
        }
    
    def create_workflow(
        self,
        user_id: UUID,
        name: str,
        workflow_type: str,
        definition: Dict[str, Any],
        execution_mode: str = "sequential"
    ) -> Workflow:
        """
        Create a new workflow in the database.
        
        Args:
            user_id: UUID of the user creating the workflow
            name: Name of the workflow
            workflow_type: Type of workflow (price_alert, research, rebalancing)
            definition: Workflow definition with nodes and edges
            execution_mode: "sequential" or "parallel"
            
        Returns:
            Created Workflow object
        """
        workflow = Workflow(
            user_id=user_id,
            name=name,
            workflow_type=workflow_type,
            definition=definition,
            execution_mode=execution_mode
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        
        return workflow
    
    def create_workflow_from_template(
        self,
        user_id: UUID,
        template_name: str,
        custom_name: Optional[str] = None
    ) -> Workflow:
        """
        Create a workflow from a predefined template.
        
        Args:
            user_id: UUID of the user creating the workflow
            template_name: Name of the template to use
            custom_name: Optional custom name (uses template name if not provided)
            
        Returns:
            Created Workflow object
        """
        template = get_workflow_template(template_name)
        
        workflow = Workflow(
            user_id=user_id,
            name=custom_name or template["name"],
            workflow_type=template_name,
            definition=template["definition"],
            execution_mode=template["execution_mode"]
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        
        return workflow
    
    def list_templates(self) -> Dict[str, Dict[str, str]]:
        """
        List all available workflow templates.
        
        Returns:
            Dictionary of template metadata
        """
        return list_workflow_templates()
    
    def get_user_workflows(self, user_id: UUID) -> List[Workflow]:
        """
        Get all workflows for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of Workflow objects
        """
        return self.db.query(Workflow).filter(
            Workflow.user_id == user_id
        ).all()
    
    def get_workflow_executions(
        self,
        workflow_id: UUID,
        limit: int = 10
    ) -> List[WorkflowExecution]:
        """
        Get recent executions for a workflow.
        
        Args:
            workflow_id: UUID of the workflow
            limit: Maximum number of executions to return
            
        Returns:
            List of WorkflowExecution objects
        """
        return self.db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).order_by(
            WorkflowExecution.created_at.desc()
        ).limit(limit).all()
