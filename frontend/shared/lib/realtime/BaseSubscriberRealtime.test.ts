import { expect, it } from "vitest";
import { BaseSubscriberRealtime } from "./BaseSubscriberRealtime";

class Subscriber extends BaseSubscriberRealtime<{ cash_update: { cash: string } }> {
  sent: string[][] = [];
  connect() { this.setConnected(true); }
  disconnect() { this.setConnected(false); }
  send() {}
  protected async updateBackendSubscription() { this.sent.push([...this.getSubscribedEvents()]); }
}

it("refaz a assinatura quando reconecta mesmo sem mudar os eventos", async () => {
  const subscriber = new Subscriber();
  subscriber.subscribe("cash_update", () => {});
  subscriber.connect();
  await Promise.resolve();
  const sent = subscriber.sent.length;
  subscriber.disconnect();
  subscriber.connect();
  await Promise.resolve();
  expect(subscriber.sent).toHaveLength(sent + 1);
  expect(subscriber.sent.at(-1)).toEqual(["cash_update"]);
});
