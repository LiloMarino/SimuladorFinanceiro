// Cursor desenhado na página: o Chromium headless grava a tela sem o cursor do sistema.
// Segue o mouse do Playwright e pulsa um anel a cada clique.
(() => {
  const install = () => {
    const style = document.createElement("style");
    style.textContent = `
      #demo-cursor {
        position: fixed; left: 0; top: 0; width: 26px; height: 26px;
        pointer-events: none; z-index: 2147483647;
        transform: translate(-100px, -100px);
        filter: drop-shadow(0 2px 3px rgb(0 0 0 / 0.35));
      }
      #demo-cursor[hidden] { display: none; }
      .demo-click {
        position: fixed; width: 40px; height: 40px; margin: -20px 0 0 -20px;
        border-radius: 50%; border: 3px solid rgb(59 130 246 / 0.9);
        pointer-events: none; z-index: 2147483646;
        animation: demo-click 450ms ease-out forwards;
      }
      @keyframes demo-click {
        from { transform: scale(0.3); opacity: 1; }
        to { transform: scale(1.4); opacity: 0; }
      }
    `;
    document.head.appendChild(style);

    const cursor = document.createElement("div");
    cursor.id = "demo-cursor";
    cursor.innerHTML = `
      <svg viewBox="0 0 24 24" width="26" height="26">
        <path d="M4 2 L4 19 L8.5 14.8 L11.6 21.6 L14.6 20.3 L11.6 13.6 L17.8 13.6 Z"
              fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/>
      </svg>`;
    document.body.appendChild(cursor);

    // A ponta da seta fica em (4, 2) do SVG
    window.addEventListener(
      "mousemove",
      (e) => (cursor.style.transform = `translate(${e.clientX - 4}px, ${e.clientY - 2}px)`),
      true,
    );
    window.addEventListener(
      "mousedown",
      (e) => {
        const ring = document.createElement("div");
        ring.className = "demo-click";
        ring.style.left = `${e.clientX}px`;
        ring.style.top = `${e.clientY}px`;
        document.body.appendChild(ring);
        setTimeout(() => ring.remove(), 500);
      },
      true,
    );
  };

  if (document.body) install();
  else document.addEventListener("DOMContentLoaded", install);
})();
