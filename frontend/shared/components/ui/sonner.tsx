import { Toaster as Sonner, type ToasterProps } from "sonner";
import { CircleCheckIcon, InfoIcon, TriangleAlertIcon, OctagonXIcon, Loader2Icon } from "lucide-react";

const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      theme="light"
      className="toaster group"
      icons={{
        success: <CircleCheckIcon className="size-4 text-toast-success" />,
        info: <InfoIcon className="size-4 text-toast-info" />,
        warning: <TriangleAlertIcon className="size-4 text-toast-warning" />,
        error: <OctagonXIcon className="size-4 text-toast-error" />,
        loading: <Loader2Icon className="size-4 animate-spin text-toast-info" />,
      }}
      style={
        {
          "--normal-bg": "var(--toast)",
          "--normal-text": "var(--toast-foreground)",
          "--normal-border": "var(--toast)",
          "--border-radius": "10px",
        } as React.CSSProperties
      }
      toastOptions={{
        classNames: {
          toast: "cn-toast shadow-[0_8px_24px_rgba(15,23,41,.18)]",
          description: "text-toast-muted!",
          actionButton: "bg-transparent! font-semibold! text-toast-info!",
        },
      }}
      {...props}
    />
  );
};

export { Toaster };
