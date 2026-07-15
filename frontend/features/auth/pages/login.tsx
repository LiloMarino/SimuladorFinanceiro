import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form, FormField, FormItem, FormLabel, FormMessage, FormControl } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/ui/card";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/components/ui/alert-dialog";
import ApiError from "@/shared/lib/models/ApiError";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { User } from "@/types";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";

// Validação com Zod
const nicknameSchema = z.object({
  nickname: z.string().min(1, "Digite um nickname!"),
});

type NicknameForm = z.infer<typeof nicknameSchema>;

export function LoginPage() {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);

  const { mutateAsync: registerNickname, isPending: registerNicknameLoading } = useApiMutation({
    mutationFn: (body: { nickname: string }) => apiFetch<User>("/api/user/register", { method: "POST", body }),
    onSuccess: () => {
      toast.success("Nickname registrado!");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const { mutateAsync: claimNickname, isPending: claimNicknameLoading } = useApiMutation({
    mutationFn: (body: { nickname: string }) => apiFetch<User>("/api/user/claim", { method: "POST", body }),
    onSuccess: () => {
      toast.success("Nickname recuperado!");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const form = useForm<NicknameForm>({
    resolver: zodResolver(nicknameSchema),
    defaultValues: { nickname: "" },
  });

  const onSubmit = async (values: NicknameForm) => {
    try {
      await registerNickname(values);
      queryClient.invalidateQueries({ queryKey: queryKeys.authSession() });
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setModalOpen(true);
      } else {
        throw err;
      }
    }
  };

  const confirmClaim = async () => {
    const nickname = form.getValues("nickname");
    await claimNickname({ nickname });
    queryClient.invalidateQueries({ queryKey: queryKeys.authSession() });
    setModalOpen(false);
  };

  const loading = registerNicknameLoading || claimNicknameLoading;
  return (
    <section className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-xl">
        <CardHeader>
          <CardTitle className="text-center text-2xl">Entrar na Sala</CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="nickname"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Seu Nickname</FormLabel>
                    <FormControl>
                      <Input placeholder="Digite seu nickname" {...field} disabled={loading} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={loading}>
                Entrar
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {/* Modal de Claim */}
      <AlertDialog open={modalOpen} onOpenChange={setModalOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Nickname já existe</AlertDialogTitle>
          </AlertDialogHeader>

          <p>
            O usuário <strong>{form.getValues("nickname")}</strong> já existe. Deseja clamar este nickname?
          </p>

          <div className="flex justify-end gap-3 mt-4">
            <AlertDialogCancel asChild>
              <Button variant="secondary">Cancelar</Button>
            </AlertDialogCancel>

            <AlertDialogAction asChild>
              <Button onClick={confirmClaim}>Sim</Button>
            </AlertDialogAction>
          </div>
        </AlertDialogContent>
      </AlertDialog>
    </section>
  );
}
