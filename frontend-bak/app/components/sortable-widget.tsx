"use client";

import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical } from "lucide-react";
import { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface SortableWidgetProps {
  id: string;
  children: ReactNode;
  isEditing: boolean;
}

export function SortableWidget({ id, children, isEditing }: SortableWidgetProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 10 : 1,
  };

  // Animation variants
  const widgetVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.3,
      }
    }
  };

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      initial="hidden"
      animate="visible"
      variants={widgetVariants}
      className={cn(
        "relative",
        isDragging && "opacity-50"
      )}
    >
      {isEditing && (
        <div
          {...attributes}
          {...listeners}
          className="absolute top-0 right-0 p-1 cursor-grab active:cursor-grabbing z-10"
        >
          <GripVertical className="w-5 h-5 text-gray-400" />
        </div>
      )}
      {children}
    </motion.div>
  );
}
