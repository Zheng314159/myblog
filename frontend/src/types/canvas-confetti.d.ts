declare module "canvas-confetti" {
  interface ConfettiOptions {
    particleCount?: number;
    spread?: number;
    origin?: { x: number; y: number };
    [key: string]: any;
  }

  type Confetti = (options?: ConfettiOptions) => void;

  const confetti: Confetti;
  export default confetti;
}
