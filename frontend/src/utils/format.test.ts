import { describe, test, expect, afterEach } from 'vitest';
import { formatNumber, UI_LOCALE } from './format';

describe('formatNumber', () => {
  test('1. Aplica el separador de miles espanol a numeros grandes', () => {
    expect(formatNumber(999999)).toBe('999.999');
    expect(formatNumber(88888)).toBe('88.888');
    expect(formatNumber(54321)).toBe('54.321');
  });

  test('2. Formatea cero y valores pequenos sin adornos', () => {
    expect(formatNumber(0)).toBe('0');
    expect(formatNumber(1)).toBe('1');
    expect(formatNumber(12)).toBe('12');
    expect(formatNumber(999)).toBe('999');
  });

  test('3. Agrupa tambien los numeros de cuatro digitos', () => {
    // El estandar espanol (CLDR, minimumGroupingDigits = 2) los dejaria sin
    // separador, pero el helper fuerza `useGrouping` para que el criterio sea
    // uniforme en toda la interfaz.
    expect(formatNumber(1000)).toBe('1.000');
    expect(formatNumber(1240)).toBe('1.240');
    expect(formatNumber(9999)).toBe('9.999');
    expect(formatNumber(10000)).toBe('10.000');
  });

  test('4. Agrupa correctamente los numeros muy grandes', () => {
    expect(formatNumber(1234567)).toBe('1.234.567');
    expect(formatNumber(1234567890)).toBe('1.234.567.890');
    expect(formatNumber(Number.MAX_SAFE_INTEGER)).toBe('9.007.199.254.740.991');
  });

  test('5. Conserva el signo de los numeros negativos', () => {
    expect(formatNumber(-1)).toBe('-1');
    expect(formatNumber(-54321)).toBe('-54.321');
  });

  test('6. Usa la coma como separador decimal, solo cuando hay decimales', () => {
    expect(formatNumber(0.5)).toBe('0,5');
    expect(formatNumber(2.25)).toBe('2,25');
    expect(formatNumber(1234.5)).toBe('1.234,5');
    // Intl redondea a un maximo de tres decimales por defecto.
    expect(formatNumber(1234.5678)).toBe('1.234,568');
  });

  test('7. Los enteros nunca arrastran decimales', () => {
    expect(formatNumber(42)).not.toContain(',');
    expect(formatNumber(1000000)).toBe('1.000.000');
  });

  test('8. Expone el locale unico de la interfaz', () => {
    expect(UI_LOCALE).toBe('es-ES');
  });
});

describe('formatNumber es independiente del locale del sistema', () => {
  const original = Number.prototype.toLocaleString;

  afterEach(() => {
    Number.prototype.toLocaleString = original;
  });

  test('9. Mantiene el formato espanol aunque el sistema use locale ingles', () => {
    // Simula un runner de CI (ubuntu-latest resuelve 'en-US'): toda llamada
    // SIN locale explicito pasa a comportarse como inglesa. Si alguien
    // regresara a `toLocaleString()` sin argumento, este test lo detectaria.
    Number.prototype.toLocaleString = function (
      this: number,
      locales?: Intl.LocalesArgument,
      options?: Intl.NumberFormatOptions,
    ): string {
      return original.call(this, locales ?? 'en-US', options);
    };

    // Control: la simulacion esta activa.
    expect((999999).toLocaleString()).toBe('999,999');

    // El helper no se ve afectado porque fija el locale de forma explicita.
    expect(formatNumber(999999)).toBe('999.999');
    expect(formatNumber(88888)).toBe('88.888');
    expect(formatNumber(54321)).toBe('54.321');
  });
});
