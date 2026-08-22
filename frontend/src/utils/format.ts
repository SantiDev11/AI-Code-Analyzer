/**
 * Utilidades de formateo de datos para la interfaz de usuario.
 */

/**
 * Convierte una cantidad de bytes a una representacion legible (B, KB, MB, GB, TB).
 *
 * @param bytes Cantidad de bytes en entero o flotante.
 * @param decimals Cantidad de decimales deseados (por defecto 1).
 * @returns Cadena formateada (ej. '8.4 MB', '512 KB', '0 B').
 */
export function formatBytes(bytes: number, decimals = 1): string {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return '0 B';
  }

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const safeIndex = Math.min(i, sizes.length - 1);
  const value = bytes / Math.pow(k, safeIndex);

  // Si el valor es entero tras redondear, omitir el decimal (.0)
  const formatted =
    value % 1 === 0 ? value.toFixed(0) : value.toFixed(dm);

  return `${formatted} ${sizes[safeIndex]}`;
}
