import React from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, Trash2 } from 'lucide-react';
import type { Grade } from '../../types';

interface GradeListProps {
  grades: Grade[];
  onReorder: (newGrades: Grade[]) => void;
  onSelect: (grade: Grade) => void;
  selectedGradeId?: string;
  onDelete: (gradeId: string) => void;
}

interface SortableGradeItemProps {
  grade: Grade;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: (id: string) => void;
}

function SortableGradeItem({ grade, isSelected, onSelect, onDelete }: SortableGradeItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id: grade.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center p-3 mb-2 bg-white rounded-lg border cursor-pointer hover:border-blue-300 transition-colors ${
        isSelected ? 'border-blue-500 ring-1 ring-blue-500 bg-blue-50' : 'border-gray-200'
      }`}
      onClick={onSelect}
    >
      <div {...attributes} {...listeners} className="cursor-grab text-gray-400 hover:text-gray-600 mr-3">
        <GripVertical size={20} />
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="font-medium text-gray-900 truncate">{grade.name}</h3>
        {grade.description && (
          <p className="text-xs text-gray-500 truncate">{grade.description}</p>
        )}
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          if (confirm('Are you sure you want to delete this grade?')) {
            onDelete(grade.id);
          }
        }}
        className="ml-2 text-gray-400 hover:text-red-500 p-1 rounded hover:bg-red-50 transition-colors"
        aria-label="Delete grade"
      >
        <Trash2 size={18} />
      </button>
    </div>
  );
}

export function GradeList({ grades, onReorder, onSelect, selectedGradeId, onDelete }: GradeListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = grades.findIndex((g) => g.id === active.id);
      const newIndex = grades.findIndex((g) => g.id === over.id);

      const newGrades = arrayMove(grades, oldIndex, newIndex);
      // Update sequence_order locally for optimistic UI
      const updatedGrades = newGrades.map((g, i) => ({ ...g, sequence_order: i }));
      onReorder(updatedGrades);
    }
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <SortableContext
        items={grades.map((g) => g.id)}
        strategy={verticalListSortingStrategy}
      >
        <div className="space-y-2">
          {grades.map((grade) => (
            <SortableGradeItem
              key={grade.id}
              grade={grade}
              isSelected={selectedGradeId === grade.id}
              onSelect={() => onSelect(grade)}
              onDelete={onDelete}
            />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}
