import React, { useState } from 'react'
import { CheckCircle2, Plus, Pencil, Trash2 } from 'lucide-react'
import type { Grade, Skill } from '../../types'

interface SkillListProps {
  grade: Grade
  onAddSkill: () => void
  onEditSkill: (skill: Skill) => void
  onDeleteSkill: (skill: Skill) => void
}

export function SkillList({ grade, onAddSkill, onEditSkill, onDeleteSkill }: SkillListProps) {
  const [hoveredSkill, setHoveredSkill] = useState<string | null>(null)

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 h-full flex flex-col">
      <div className="flex justify-between items-center mb-6 border-b border-gray-100 pb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">{grade.name}</h2>
          {grade.description && <p className="text-gray-500 mt-1">{grade.description}</p>}
        </div>
        <button
          onClick={onAddSkill}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={18} />
          <span>Add Skill</span>
        </button>
      </div>

      <div className="flex-1 overflow-auto">
        {grade.skills && grade.skills.length > 0 ? (
          <div className="space-y-3">
            {grade.skills.map((skill) => (
              <div
                key={skill.id}
                className="flex items-start justify-between p-4 bg-gray-50 rounded-lg border border-gray-100 hover:border-blue-100 transition-colors group"
                onMouseEnter={() => setHoveredSkill(skill.id)}
                onMouseLeave={() => setHoveredSkill(null)}
              >
                <div className="flex items-start">
                  <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                  <div>
                    <h3 className="font-medium text-gray-900">{skill.name}</h3>
                    {skill.description && (
                      <p className="text-sm text-gray-500 mt-1">{skill.description}</p>
                    )}
                  </div>
                </div>
                <div
                  className={`flex space-x-2 ${hoveredSkill === skill.id ? 'opacity-100' : 'opacity-0'} transition-opacity`}
                >
                  <button
                    onClick={() => onEditSkill(skill)}
                    className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                    aria-label="Edit skill"
                  >
                    <Pencil size={16} />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      if (confirm('Are you sure you want to delete this skill?')) {
                        onDeleteSkill(skill)
                      }
                    }}
                    className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                    aria-label="Delete skill"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-400">
            <p className="text-lg">No skills defined for this grade yet.</p>
            <p className="text-sm mt-2">Click "Add Skill" to get started.</p>
          </div>
        )}
      </div>
    </div>
  )
}
