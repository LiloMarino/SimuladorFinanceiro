import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser } from "@fortawesome/free-solid-svg-icons";
import type { Player } from "@/types";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/components/ui/form";
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

// Validação com Zod
const nicknameSchema = z.object({
  nickname: z.string().min(1, "Digite um nickname!"),
});

type NicknameForm = z.infer<typeof nicknameSchema>;

export function LoginPage({
  players = [
    { name: "TraderPro", status: "Conectado", color: "blue" },
    { name: "InvestAnjo", status: "Conectado", color: "purple" },
  ],
}: {
  players: Player[];
}) {
  const [modalOpen, setModalOpen] = useState(false);
  const [nicknameToClaim, setNicknameToClaim] = useState("");

  const form = useForm<NicknameForm>({
    resolver: zodResolver(nicknameSchema),
    defaultValues: { nickname: "" },
  });

  const onSubmit = (values: NicknameForm) => {
    setNicknameToClaim(values.nickname);
    setModalOpen(true);
  };

  const confirmClaim = () => {
    setModalOpen(false);
    alert(`Entrando como ${nicknameToClaim}!`);
    // Aqui chamaria API para registrar/claimar nickname
  };

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
                      <Input placeholder="Digite seu nickname" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700">
                Entrar
              </Button>
            </form>
          </Form>

          <h3 className="font-medium mb-3">Jogadores na Sala</h3>
          <div className="border rounded-lg overflow-hidden">
            {players.length === 0 && <p className="p-3 text-gray-400">Nenhum jogador ainda...</p>}

            <div className="divide-y divide-gray-200">
              {players.map((p) => (
                <div key={p.name} className="p-3 flex items-center justify-between">
                  <div className="flex items-center">
                    <FontAwesomeIcon icon={faUser} className={`mr-2 text-${p.color}-600`} />
                    <span>{p.name}</span>
                  </div>
                  <span className="text-sm text-gray-500">{p.status}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <AlertDialog open={modalOpen} onOpenChange={setModalOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar Nickname</AlertDialogTitle>
          </AlertDialogHeader>

          <p>
            O usuário <strong>{nicknameToClaim}</strong> já existe. Deseja clamar este nickname?
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
