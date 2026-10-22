import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { DoorClosed, UsersRound } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Spinner } from "@/shared/components/ui/spinner";
import { useAuth } from "@/shared/hooks/useAuth";
import { LoginShowcase } from "../components/login-showcase";
import { useClaimUser } from "../hooks/mutations/useClaimUser";
import { useRegisterUser } from "../hooks/mutations/useRegisterUser";

const nicknameSchema = z.object({
  nickname: z
    .string()
    .trim()
    .min(1, "Escolha um nome para entrar.")
    .regex(/^[^#]+$/, "Tire o # do nome: ele é reservado para identificar a partida."),
});

type NicknameForm = z.infer<typeof nicknameSchema>;

// A sala recusa a entrada com 423: sala cheia ou partida sem vaga
const ROOM_CLOSED_STATUS = 423;

export function LoginPage() {
  const { entryError } = useAuth();
  // Nickname que já tem conta: a decisão (é você ou não) acontece dentro do card
  const [taken, setTaken] = useState<string | null>(null);

  const register = useRegisterUser();
  const claim = useClaimUser();

  const form = useForm<NicknameForm>({
    resolver: zodResolver(nicknameSchema),
    defaultValues: { nickname: "" },
  });

  const chooseAnotherName = () => {
    setTaken(null);
    claim.reset();
    register.reset();
  };

  const busy = register.isPending || claim.isPending;
  const registerFailed =
    register.isError && register.error.status !== 409 && register.error.status !== ROOM_CLOSED_STATUS;
  const roomClosed = [entryError, register.error, claim.error].find((e) => e?.status === ROOM_CLOSED_STATUS);

  return (
    <div className="flex min-h-svh">
      <LoginShowcase />

      <main className="flex flex-1 items-center justify-center p-10">
        <Card size="lg" className="w-full max-w-[400px]">
          <CardHeader>
            <CardTitle role="heading" aria-level={1}>
              Entrar na sala
            </CardTitle>
            <CardDescription>
              Primeira vez aqui? Escolha um nome. Já jogou? Use o mesmo para recuperar suas partidas.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form
              onSubmit={(event) =>
                void form.handleSubmit((values) =>
                  register.mutate(values, {
                    onError: (err, body) => {
                      if (err.status === 409) setTaken(body.nickname);
                    },
                  }),
                )(event)
              }
              className="grid gap-5"
            >
              <Controller
                control={form.control}
                name="nickname"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="nickname">Seu nickname</FieldLabel>
                    <Input
                      {...field}
                      id="nickname"
                      fieldSize="lg"
                      autoComplete="off"
                      aria-invalid={fieldState.invalid}
                      disabled={busy}
                      onChange={(e) => {
                        field.onChange(e);
                        if (taken) chooseAnotherName();
                      }}
                    />
                    {fieldState.invalid ? (
                      <FieldError errors={[fieldState.error]} />
                    ) : (
                      <FieldDescription>É assim que você aparece no ranking. Não use #.</FieldDescription>
                    )}
                  </Field>
                )}
              />

              {/* Nickname já existe: um aviso só, com as duas saídas */}
              {taken ? (
                <Alert variant={claim.isError ? "destructive" : "info"}>
                  <UsersRound />
                  <AlertTitle>{taken} já tem conta nesta sala</AlertTitle>
                  <AlertDescription>
                    {claim.isError
                      ? claim.error.message
                      : "Se é você, entre e continue de onde parou. Se não, escolha outro nome."}
                  </AlertDescription>
                  <div className="col-span-full mt-2 flex gap-2">
                    <Button
                      type="button"
                      className="flex-1"
                      disabled={busy}
                      onClick={() => claim.mutate({ nickname: taken })}
                    >
                      {claim.isPending && <Spinner />}
                      Sou eu, entrar
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      className="flex-1"
                      onClick={() => {
                        chooseAnotherName();
                        form.setFocus("nickname");
                      }}
                    >
                      Usar outro nome
                    </Button>
                  </div>
                </Alert>
              ) : (
                <Button type="submit" size="lg" disabled={busy}>
                  {register.isPending && <Spinner />}
                  {register.isPending ? "Entrando…" : "Entrar"}
                </Button>
              )}

              {roomClosed && (
                <Alert variant="warning">
                  <DoorClosed />
                  <AlertTitle>Não dá pra entrar agora</AlertTitle>
                  <AlertDescription>{roomClosed.message}</AlertDescription>
                </Alert>
              )}

              {registerFailed && (
                <Alert variant="destructive">
                  <AlertTitle>{register.error.message}</AlertTitle>
                  <AlertDescription>{register.error.statusLine}</AlertDescription>
                </Alert>
              )}
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
