import { Spinner } from "@/shared/components/ui/spinner";
import { cn } from "@/shared/lib/utils";

type LoadingPageProps = {
  variant?: "page" | "fullscreen";
  className?: string;
};

export function LoadingPage({ variant = "page", className }: LoadingPageProps) {
  return (
    <section
      className={cn(
        "flex items-center justify-center",
        variant === "page" && "min-h-[80vh]",
        variant === "fullscreen" && "w-screen h-screen",
        className
      )}
    >
      <Spinner className="h-8 w-8 text-muted-foreground" />
    </section>
  );
}
