import React, { useEffect, useState, useCallback } from 'react'
import axios from 'axios'
import { Plus, GripVertical } from 'lucide-react'
import { GradeList } from '../components/grades/GradeList'
import { SkillList } from '../components/grades/SkillList'
import { Modal } from '../components/Modal'
import type { Grade, GradeCreate, SkillCreate, Skill } from '../types'

export default function GradesPage() {
  const [grades, setGrades] = useState<Grade[]>([])
  const [selectedGradeId, setSelectedGradeId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Modals state
  const [isGradeModalOpen, setIsGradeModalOpen] = useState(false)
  const [isSkillModalOpen, setIsSkillModalOpen] = useState(false)
  const [editingSkill, setEditingSkill] = useState<Skill | null>(null)

  // Form state
  const [gradeName, setGradeName] = useState('')
  const [gradeDesc, setGradeDesc] = useState('')
  const [skillName, setSkillName] = useState('')
  const [skillDesc, setSkillDesc] = useState('')

  const fetchGrades = useCallback(async () => {
    try {
      setLoading(true)
      const res = await axios.get('/api/grades/')
      setGrades(res.data)
      if (res.data.length > 0) {
        setSelectedGradeId((prev) => {
          if (prev && res.data.some((g: Grade) => g.id === prev)) return prev
          return res.data[0].id
        })
      }
    } catch (err) {
      console.error(err)
      setError('Failed to load grades')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchGrades()
  }, [fetchGrades])

  const handleReorder = async (newGrades: Grade[]) => {
    const originalGrades = [...grades]
    setGrades(newGrades)
    try {
      await axios.patch('/api/grades/reorder', {
        ordered_ids: newGrades.map((g) => g.id),
      })
    } catch (err) {
      console.error('Failed to save order', err)
      setGrades(originalGrades) // Revert
    }
  }

  const handleCreateGrade = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!gradeName.trim()) return

    try {
      const payload: GradeCreate = { name: gradeName, description: gradeDesc }
      const res = await axios.post('/api/grades/', payload)
      setGrades([...grades, res.data])
      setSelectedGradeId(res.data.id)
      setIsGradeModalOpen(false)
      setGradeName('')
      setGradeDesc('')
    } catch (err) {
      console.error(err)
      alert('Failed to create grade')
    }
  }

  const handleSaveSkill = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!skillName.trim() || !selectedGradeId) return

    try {
      const payload: SkillCreate = { name: skillName, description: skillDesc }

      if (editingSkill) {
        // Update existing skill
        const res = await axios.put(`/api/grades/skills/${editingSkill.id}`, payload)
        const updatedSkill = res.data

        const newGrades = grades.map((g) => {
          if (g.id === selectedGradeId) {
            return {
              ...g,
              skills: g.skills.map((s) => (s.id === updatedSkill.id ? updatedSkill : s)),
            }
          }
          return g
        })
        setGrades(newGrades)
      } else {
        // Create new skill
        const res = await axios.post(`/api/grades/${selectedGradeId}/skills`, payload)
        const newSkill = res.data

        const newGrades = grades.map((g) => {
          if (g.id === selectedGradeId) {
            return { ...g, skills: [...(g.skills || []), newSkill] }
          }
          return g
        })
        setGrades(newGrades)
      }

      setIsSkillModalOpen(false)
      setEditingSkill(null)
      setSkillName('')
      setSkillDesc('')
    } catch (err) {
      console.error(err)
      alert(editingSkill ? 'Failed to update skill' : 'Failed to add skill')
    }
  }

  const openAddSkillModal = () => {
    setEditingSkill(null)
    setSkillName('')
    setSkillDesc('')
    setIsSkillModalOpen(true)
  }

  const openEditSkillModal = (skill: Skill) => {
    setEditingSkill(skill)
    setSkillName(skill.name)
    setSkillDesc(skill.description || '')
    setIsSkillModalOpen(true)
  }

  const handleDeleteSkill = async (skill: Skill) => {
    try {
      await axios.delete(`/api/grades/skills/${skill.id}`)
      const newGrades = grades.map((g) => {
        if (g.id === skill.grade_id) {
          return {
            ...g,
            skills: g.skills.filter((s) => s.id !== skill.id),
          }
        }
        return g
      })
      setGrades(newGrades)
    } catch (err) {
      console.error(err)
      alert('Failed to delete skill')
    }
  }

  const handleDeleteGrade = async (gradeId: string) => {
    try {
      await axios.delete(`/api/grades/${gradeId}`)
      const newGrades = grades.filter((g) => g.id !== gradeId)
      setGrades(newGrades)
      if (selectedGradeId === gradeId) {
        setSelectedGradeId(newGrades.length > 0 ? newGrades[0].id : null)
      }
    } catch (err) {
      console.error(err)
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        alert('Cannot delete grade: It is assigned to riders (past or present).')
      } else {
        alert('Failed to delete grade')
      }
    }
  }

  const selectedGrade = grades.find((g) => g.id === selectedGradeId)

  if (loading && grades.length === 0)
    return <div className="p-8 text-center text-gray-500">Loading curriculum...</div>
  if (error) return <div className="p-8 text-red-500 text-center">{error}</div>

  return (
    <div className="p-8 h-full flex flex-col max-h-screen overflow-hidden">
      <div className="flex justify-between items-center mb-6 flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Curriculum Builder</h1>
          <p className="text-gray-600">Define the progression path for your school.</p>
        </div>
        <button
          onClick={() => setIsGradeModalOpen(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-sm"
        >
          <Plus size={18} />
          <span>Add Grade</span>
        </button>
      </div>

      <div className="flex-1 flex space-x-6 min-h-0">
        {/* Left Sidebar: Grades List */}
        <div className="w-1/3 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col overflow-hidden">
          <div className="p-4 border-b border-gray-100 bg-gray-50">
            <h2 className="font-semibold text-gray-700 flex items-center">
              <GripVertical size={16} className="mr-2 text-gray-400" />
              Grades Order
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <GradeList
              grades={grades}
              onReorder={handleReorder}
              onSelect={(g) => setSelectedGradeId(g.id)}
              selectedGradeId={selectedGradeId || undefined}
              onDelete={handleDeleteGrade}
            />
            {grades.length === 0 && (
              <div className="text-center py-8 text-gray-400 text-sm">
                No grades yet. Create one to start.
              </div>
            )}
          </div>
        </div>

        {/* Main Panel: Skills */}
        <div className="w-2/3 flex flex-col h-full overflow-hidden">
          {selectedGrade ? (
            <SkillList
              grade={selectedGrade}
              onAddSkill={openAddSkillModal}
              onEditSkill={openEditSkillModal}
              onDeleteSkill={handleDeleteSkill}
            />
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 h-full flex flex-col items-center justify-center text-gray-400">
              <div className="p-6 bg-gray-50 rounded-full mb-4">
                <GripVertical size={48} className="text-gray-300" />
              </div>
              <p className="text-lg font-medium">Select a grade to manage skills</p>
              <p className="text-sm mt-1">Or create a new one</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Grade Modal */}
      <Modal
        isOpen={isGradeModalOpen}
        onClose={() => setIsGradeModalOpen(false)}
        title="Add New Grade"
      >
        <form onSubmit={handleCreateGrade} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Grade Name</label>
            <input
              type="text"
              required
              value={gradeName}
              onChange={(e) => setGradeName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              placeholder="e.g. Grade 1 - Beginner"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={gradeDesc}
              onChange={(e) => setGradeDesc(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              placeholder="Brief description of requirements..."
              rows={3}
            />
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => setIsGradeModalOpen(false)}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-sm"
            >
              Create Grade
            </button>
          </div>
        </form>
      </Modal>

      {/* Add/Edit Skill Modal */}
      <Modal
        isOpen={isSkillModalOpen}
        onClose={() => setIsSkillModalOpen(false)}
        title={editingSkill ? 'Edit Skill' : `Add Skill to ${selectedGrade?.name || ''}`}
      >
        <form onSubmit={handleSaveSkill} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Skill Name</label>
            <input
              type="text"
              required
              value={skillName}
              onChange={(e) => setSkillName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              placeholder="e.g. Rising Trot"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={skillDesc}
              onChange={(e) => setSkillDesc(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              placeholder="Specific criteria for this skill..."
              rows={3}
            />
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => setIsSkillModalOpen(false)}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-sm"
            >
              {editingSkill ? 'Save Changes' : 'Add Skill'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
