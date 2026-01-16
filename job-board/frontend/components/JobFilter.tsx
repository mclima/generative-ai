"use client";

type FilterProps = {
  onFilterChange: (role: string | null) => void;
  selectedRole: string | null;
};

const roleCategories = [
  { value: null, label: "All Jobs", emoji: "🌐" },
  { value: "ai", label: "AI & ML", emoji: "🤖" },
  { value: "frontend", label: "Frontend", emoji: "🎨" },
  { value: "backend", label: "Backend", emoji: "⚙️" },
  { value: "fullstack", label: "Full Stack", emoji: "🔧" },
  { value: "devops", label: "DevOps", emoji: "🚀" },
  { value: "engineering", label: "Engineering", emoji: "👷" },
];

export default function JobFilter({ onFilterChange, selectedRole }: FilterProps) {
  const handleFilterClick = (role: string | null) => {
    onFilterChange(role);
  };

  return (
    <nav 
      aria-label="Job category filters"
      style={{
        marginBottom: "2rem",
        overflowX: "auto",
        paddingBottom: "0.5rem",
      }}
    >
      <div style={{
        display: "flex",
        gap: "0.75rem",
        flexWrap: "wrap",
      }}>
        {roleCategories.map((category) => (
          <button
            key={category.value || "all"}
            onClick={() => handleFilterClick(category.value)}
            aria-pressed={selectedRole === category.value}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "1px solid",
              borderColor: selectedRole === category.value ? "#3b82f6" : "#333",
              backgroundColor: selectedRole === category.value ? "#1e3a8a" : "#0f0f0f",
              color: selectedRole === category.value ? "#93c5fd" : "#ccc",
              cursor: "pointer",
              fontSize: "0.875rem",
              fontWeight: selectedRole === category.value ? "600" : "400",
              transition: "all 0.2s",
              whiteSpace: "nowrap",
            }}
            onMouseEnter={(e) => {
              if (selectedRole !== category.value) {
                e.currentTarget.style.borderColor = "#555";
                e.currentTarget.style.backgroundColor = "#1a1a1a";
              }
            }}
            onMouseLeave={(e) => {
              if (selectedRole !== category.value) {
                e.currentTarget.style.borderColor = "#333";
                e.currentTarget.style.backgroundColor = "#0f0f0f";
              }
            }}
          >
            <span style={{ marginRight: "0.5rem" }}>{category.emoji}</span>
            {category.label}
          </button>
        ))}
      </div>
    </nav>
  );
}
