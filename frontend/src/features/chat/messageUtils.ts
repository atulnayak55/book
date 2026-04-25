import type { WebSocketMessage } from "../../hooks/useWebSocket";
import type { MessageResponse } from "./api";

export type ChatMessage = MessageResponse | WebSocketMessage;

export function getMessageTimestampValue(message: Pick<ChatMessage, "timestamp">): number {
  if (!message.timestamp) {
    return 0;
  }

  const value = new Date(message.timestamp).getTime();
  return Number.isNaN(value) ? 0 : value;
}

export function mergeChatMessages(
  history: MessageResponse[] = [],
  liveMessages: WebSocketMessage[] = [],
): ChatMessage[] {
  const seenIds = new Set<number>();

  return [...history, ...liveMessages]
    .filter((message) => {
      if (message.id === undefined) {
        return true;
      }
      if (seenIds.has(message.id)) {
        return false;
      }
      seenIds.add(message.id);
      return true;
    })
    .sort((left, right) => {
      const timeDelta = getMessageTimestampValue(left) - getMessageTimestampValue(right);
      if (timeDelta !== 0) {
        return timeDelta;
      }

      return (left.id ?? 0) - (right.id ?? 0);
    });
}
