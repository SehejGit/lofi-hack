import React from 'react'
import { cn } from "@/lib/utils"

interface ShinyBorderProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  className?: string
}

export function ShinyBorder({ children, className, ...props }: ShinyBorderProps) {
  return (
    <button
      className={cn(
        "relative group/btn overflow-hidden rounded-lg",
        "before:absolute before:w-full before:h-full before:bg-gradient-to-r",
        "before:from-transparent before:via-white/10 before:to-transparent",
        "before:translate-x-[100%] before:group-hover/btn:translate-x-[-100%]",
        "before:transition-transform before:duration-500",
        "border border-white/20 backdrop-blur-sm",
        "px-4 py-2 text-white/80 hover:text-white transition-colors",
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}