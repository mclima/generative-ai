import Link from 'next/link'
import { MatchedJob } from '@/types'
import { formatDate, getMatchColor, getMatchBgColor } from '@/lib/utils'
import { Building2, MapPin, Calendar, Tag, TrendingUp, CheckCircle2, BarChart3, Sparkles } from 'lucide-react'

interface MatchedJobCardProps {
  job: MatchedJob
}

export default function MatchedJobCard({ job }: MatchedJobCardProps) {
  return (
    <div className={`border rounded-lg p-6 ${getMatchBgColor(job.match_score)}`}>
      <div className="flex items-start justify-between mb-4">
        <Link href={`/jobs/${job.id}`} className="flex-grow" target="_blank" rel="noopener noreferrer">
          <h3 className="text-xl font-semibold text-primary hover:underline cursor-pointer">
            {job.title}
          </h3>
        </Link>
        <div className="flex items-center gap-2 ml-4">
          <TrendingUp size={20} className={getMatchColor(job.match_score)} />
          <span className={`text-2xl font-bold ${getMatchColor(job.match_score)}`}>
            {job.match_score}%
          </span>
        </div>
      </div>
      
      <div className="mb-3">
        <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getMatchColor(job.match_score)}`}>
          {job.match_level}
        </span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
        <div className="flex items-center gap-2 text-gray-300">
          <Building2 size={16} className="text-gray-400" />
          <span className="text-sm">{job.company}</span>
        </div>
        
        <div className="flex items-center gap-2 text-gray-300">
          <MapPin size={16} className="text-gray-400" />
          <span className="text-sm">{job.location}</span>
        </div>
        
        <div className="flex items-center gap-2 text-gray-300">
          <Calendar size={16} className="text-gray-400" />
          <span className="text-sm">{formatDate(job.posted_date)}</span>
        </div>
        
        <div className="flex items-center gap-2">
          <Tag size={16} className="text-gray-400" />
          <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-medium">
            {job.category}
          </span>
        </div>
      </div>
      
      {/* Score Breakdown */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 size={16} className="text-primary" />
          <h4 className="text-sm font-semibold text-gray-200">Score Breakdown</h4>
        </div>
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-gray-800/50 rounded p-2">
            <div className="text-xs text-gray-400 mb-1">Skills</div>
            <div className="text-sm font-semibold text-primary">{job.skill_score}%</div>
            <div className="text-xs text-gray-500">40% weight</div>
          </div>
          <div className="bg-gray-800/50 rounded p-2">
            <div className="text-xs text-gray-400 mb-1">Semantic</div>
            <div className="text-sm font-semibold text-primary">{job.semantic_score}%</div>
            <div className="text-xs text-gray-500">35% weight</div>
          </div>
          <div className="bg-gray-800/50 rounded p-2">
            <div className="text-xs text-gray-400 mb-1">Title</div>
            <div className="text-sm font-semibold text-primary">{job.title_score}%</div>
            <div className="text-xs text-gray-500">25% weight</div>
          </div>
        </div>
      </div>

      {/* AI Match Explanation - Only for top matches with 80%+ score */}
      {job.match_explanation && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles size={16} className="text-yellow-400" />
            <h4 className="text-sm font-semibold text-gray-200">AI Match Insight</h4>
          </div>
          <div className="bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-lg p-4">
            <p className="text-sm text-gray-300 leading-relaxed">
              {job.match_explanation}
            </p>
          </div>
        </div>
      )}

      {/* Matched Skills */}
      {job.matched_skills && job.matched_skills.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 size={16} className="text-green-500" />
            <h4 className="text-sm font-semibold text-gray-200">
              Matched Skills ({job.matched_skills.length})
            </h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {job.matched_skills.map((skill, index) => (
              <span
                key={index}
                className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs border border-green-500/30"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
      
      <div className="text-xs text-gray-500 pt-3 mt-4 border-t border-gray-700">
        Source: {job.source}
      </div>
    </div>
  )
}
