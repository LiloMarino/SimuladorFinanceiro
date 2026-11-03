import { Dialog, DialogBody, DialogContent, DialogHeader, DialogTitle } from "@/shared/components/ui/dialog";
import type { House } from "../lib/house";
import { ElectedHouse } from "./elected-house";

type ElectedHouseDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  house: House;
};

/** Como os votos da última eleição viraram as cadeiras da casa. */
export function ElectedHouseDialog({ open, onOpenChange, house }: ElectedHouseDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent initialFocus={false} className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-150">
        <DialogHeader variant="divided">
          <DialogTitle>Como a casa foi eleita</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <ElectedHouse house={house} />
        </DialogBody>
      </DialogContent>
    </Dialog>
  );
}
