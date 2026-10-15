// OpenCode 플러그인(<repo>/.opencode/plugins/plan-capsule.js). 압축 직전 계획 캡슐을 요약 맥락에 넣고, 사용자 입력을 inbox에 남긴다.
// 근거: opencode.ai/docs/plugins 및 설치된 @opencode-ai/plugin·sdk의 chat.message/session.get 계약.
import { execFileSync } from "node:child_process";
import path from "node:path";

export const PlanCapsule = async ({ directory, client }) => {
  const cli = path.join(directory, ".plan", "bin", "plan.mjs");
  const plan = (args, input) => {
    try {
      return execFileSync("node", [cli, ...args], { cwd: directory, input, encoding: "utf8" });
    } catch (e) {
      return `[plan] 실패: ${e.message}`;
    }
  };
  return {
    "experimental.session.compacting": async (_input, output) => {
      output.context.push(plan(["inject", "--event", "compact"]));
    },
    "chat.message": async (input, output) => {
      const text = (output?.parts ?? []).filter((p) => p?.type === "text" && !p.synthetic && !p.ignored).map((p) => p.text).join("\n");
      if (!text.trim()) return;
      const sessionID = input.sessionID;
      let session;
      try { session = (await client.session.get({ path: { id: sessionID } })).data; } catch {}
      const origin = session?.parentID || (output.message?.role && output.message.role !== "user") ? "agent" : session?.id === sessionID && output.message?.role === "user" ? "user" : "unknown";
      plan(["capture", "--tool", "opencode"], JSON.stringify({ prompt: text, origin, session_id: sessionID, parent_session_id: session?.parentID, message_id: output.message?.id }));
    },
  };
};
