/**
 * Utilidades de formateo de datos para la interfaz de usuario.
 */

/**
 * Locale unico de la interfaz. Se declara aqui para que todos los helpers
 * compartan el mismo criterio y no haya que repetirlo en cada componente.
 */
export const UI_LOCALE = 'es-ES';

/**
 * Formatea un numero para mostrarlo al usuario con separador de miles espanol.
 *
 * El locale se fija de forma explicita en lugar de dejar que `toLocaleString()`
 * use el del sistema operativo: asi el resultado es identico en cualquier
 * maquina y en CI. Sin fijarlo, un runner con locale ingles renderizaria
 * '999,999' donde Windows en espanol renderiza '999.999'.
 *
 * Los enteros salen sin decimales; los valores fraccionarios conservan hasta
 * tres decimales (el maximo por defecto de Intl), asi que solo aparecen
 * decimales cuando el dato realmente los tiene.
 *
 * `useGrouping` fuerza el separador de miles tambien en los numeros de cuatro
 * digitos. Por defecto el estandar espanol los deja sin agrupar ('1240'), pero
 * aqui se prefiere un criterio unico y predecible: '1.240'.
 *
 * Se pasa el booleano `true` y no la cadena 'always' porque son equivalentes
 * (la especificacion normaliza `true` a 'always') y `true` si encaja con el
 * tipado de `lib: ES2020` que usa el proyecto, sin tener que tocar tsconfig.
 *
 * Para bytes usa `formatBytes`, y para fechas los helpers de cada componente:
 * este helper es para contadores y enteros generales.
 *
 * @param value Numero a formatear.
 * @returns Cadena formateada (ej. '999.999', '1.240', '0', '1.234,5').
 */
export function formatNumber(value: number): string {
  return value.toLocaleString(UI_LOCALE, { useGrouping: true });
}

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
