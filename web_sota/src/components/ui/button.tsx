import { cn } from "@/lib/utils";

export function Button({
  className,
  children,
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" | "danger" }) {
  const styles =
    variant === "primary"
      ? "bg-cyan-600 hover:bg-cyan-500 text-white"
      : variant === "danger"
        ? "bg-red-700 hover:bg-red-600 text-white"
        : "bg-zinc-800 hover:bg-zinc-700 text-zinc-100";
  return (
    <button
      type="button"
      className={cn("rounded-lg px-3 py-2 text-sm font-medium transition", styles, className)}
      {...props}
    >
      {children}
    </button>
  );
}
