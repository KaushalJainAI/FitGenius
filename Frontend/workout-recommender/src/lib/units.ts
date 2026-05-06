import type { MeasurementSystem } from "../contexts/ThemeContext";

const KG_TO_LB = 2.2046226218;
const CM_TO_IN = 0.3937007874;

function round(value: number, digits = 1) {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

export function displayWeight(valueKg: number | "" | null | undefined, system: MeasurementSystem) {
  if (valueKg === "" || valueKg == null) return "";
  return system === "imperial" ? round(valueKg * KG_TO_LB, 1) : round(valueKg, 1);
}

export function inputWeight(value: number | "", system: MeasurementSystem) {
  if (value === "") return "";
  return system === "imperial" ? round(value / KG_TO_LB, 1) : value;
}

export function displayHeight(valueCm: number | "" | null | undefined, system: MeasurementSystem) {
  if (valueCm === "" || valueCm == null) return "";
  return system === "imperial" ? round(valueCm * CM_TO_IN, 1) : round(valueCm, 1);
}

export function inputHeight(value: number | "", system: MeasurementSystem) {
  if (value === "") return "";
  return system === "imperial" ? round(value / CM_TO_IN, 1) : value;
}

export function weightUnit(system: MeasurementSystem) {
  return system === "imperial" ? "LB" : "KG";
}

export function heightUnit(system: MeasurementSystem) {
  return system === "imperial" ? "IN" : "CM";
}
