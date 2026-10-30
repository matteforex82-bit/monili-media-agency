// I colori più vivi di una foto, per le tessere mentre il pezzo viene lavorato.
export function photoPalette(imageUrl: string, count = 4): Promise<string[]> {
  return new Promise((resolve) => {
    const image = new Image();
    image.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = 48;
        canvas.height = 48;
        const context = canvas.getContext('2d', { willReadFrequently: true });
        if (!context) return resolve([]);
        context.drawImage(image, 0, 0, 48, 48);
        const { data } = context.getImageData(0, 0, 48, 48);
        const buckets = new Map<number, { r: number; g: number; b: number; n: number }>();
        for (let i = 0; i < data.length; i += 4) {
          const key = ((data[i] >> 5) << 6) | ((data[i + 1] >> 5) << 3) | (data[i + 2] >> 5);
          const bucket = buckets.get(key) || { r: 0, g: 0, b: 0, n: 0 };
          bucket.r += data[i];
          bucket.g += data[i + 1];
          bucket.b += data[i + 2];
          bucket.n += 1;
          buckets.set(key, bucket);
        }
        const scored = [...buckets.values()]
          .map((bucket) => {
            const [r, g, b] = [bucket.r / bucket.n, bucket.g / bucket.n, bucket.b / bucket.n];
            const high = Math.max(r, g, b);
            const saturation = high ? (high - Math.min(r, g, b)) / high : 0;
            return { r, g, b, score: high < 50 ? 0 : saturation * 0.7 + Math.min(bucket.n / 300, 0.3) };
          })
          .filter((color) => color.score > 0)
          .sort((a, b) => b.score - a.score);
        const picked: Array<{ r: number; g: number; b: number }> = [];
        for (const color of scored) {
          if (picked.every((other) => Math.abs(other.r - color.r) + Math.abs(other.g - color.g) + Math.abs(other.b - color.b) > 90)) {
            picked.push(color);
          }
          if (picked.length === count) break;
        }
        resolve(picked.map(({ r, g, b }) => `#${[r, g, b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('')}`));
      } catch {
        resolve([]);
      }
    };
    image.onerror = () => resolve([]);
    image.src = imageUrl;
  });
}
