// components/ui/Input.tsx — STYLED TEXT INPUT with optional label and error message.
//
// This wraps the plain HTML <input> with our dark-theme styling and adds two
// extra features:
//
//   label — a text label shown above the input (e.g. "Username", "Password")
//            The label is linked to the input via htmlFor/id so clicking the label
//            focuses the input (standard accessibility practice).
//
//   error — if provided, turns the input border red and shows the error text below.
//           Used to display validation errors from our JS checks or from the server.
//
// HTML validation attributes (required, minLength, maxLength, pattern, type) are
// passed straight through via "...props" — this is how we do form validation:
//
//   <Input required minLength={3} maxLength={32} pattern="[A-Za-z0-9_]+" />
//
//   required   → browser won't submit the form if this field is empty
//   minLength  → browser rejects input shorter than N characters
//   maxLength  → browser refuses to type more than N characters
//   pattern    → browser validates the value against a regex
//   type="password" → browser hides the characters with dots

import { cn } from '@/lib/utils'
import type { InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export function Input({ label, error, className, id, ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1">
      {/* Render the label only if one was provided */}
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-[#888899]">
          {label}
        </label>
      )}
      <input
        id={id}
        className={cn(
          // Base styling: dark background, rounded corners, light text
          'w-full rounded-lg border border-[#2a2a4a] bg-[#12121f] px-3 py-2 text-sm text-[#e8e8f0]',
          'placeholder:text-[#555566]',
          // Purple ring on focus
          'focus:outline-none focus:border-[#6c63ff] focus:ring-1 focus:ring-[#6c63ff]',
          'disabled:opacity-50',
          // If there is an error, swap the border and ring to red
          error && 'border-[#e05555] focus:border-[#e05555] focus:ring-[#e05555]',
          className
        )}
        {...props}
      />
      {/* Show error text in red below the input */}
      {error && <p className="text-xs text-[#e05555]">{error}</p>}
    </div>
  )
}
