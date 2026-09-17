import { bootstrapCityGraphics, createFixedStepLoop } from './city_graphics_accelerator.js';

export async function startCityApp({ step, render, selector = 'canvas[data-city-gpu]' }) {
  const graphics = await bootstrapCityGraphics({ selector, targetFps: 60, minScale: 0.55, dprCap: 2 });
  const controller = graphics.attachments[0]?.controller ?? null;
  const loop = createFixedStepLoop({ step, render, fixedDt: 1 / 60, maxCatchup: 5, controller });
  loop.start();
  return { graphics, loop };
}
