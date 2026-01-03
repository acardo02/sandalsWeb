import { writable } from 'svelte/store';

/**
 * @typedef {{
 *  id: number | string,
 *  name: string,
 *  price: number,
 *  image?: string,
 *  image_url?: string,
 *  description?: string,
 *  stock?: number
 * }} Product
 */

/**
 * @typedef {Product & { qty: number }} CartItem
 */

/** @type {import('svelte/store').Writable<CartItem[]>} */
export const cart = writable([]);

/**
 * @param {Product} product
 * @param {number} quantity - Cantidad a agregar (por defecto 1)
 * @returns {boolean} - True si se agregó exitosamente, False si no hay suficiente stock
 */
export function addToCart(product, quantity = 1) {
  let success = false;
  
  cart.update((items) => {
    const exists = items.find((p) => p.id === product.id);
    const currentQty = exists ? exists.qty : 0;
    const newQty = currentQty + quantity;

    // Validar stock si el producto tiene información de stock
    if (product.stock !== undefined && newQty > product.stock) {
      console.warn(`No hay suficiente stock. Disponible: ${product.stock}, Intentando agregar: ${newQty}`);
      success = false;
      return items; // No modificar el carrito
    }

    success = true;

    if (exists) {
      return items.map((p) =>
        p.id === product.id
          ? { ...p, qty: newQty }
          : p
      );
    }

    return [...items, { ...product, qty: quantity }];
  });

  return success;
}

/**
 * @param {number | string} id
 */
export function removeFromCart(id) {
  cart.update((items) => items.filter((p) => p.id !== id));
}

/**
 * Actualiza la cantidad de un producto en el carrito
 * @param {number | string} id
 * @param {number} newQty
 * @param {number} maxStock - Stock máximo disponible
 * @returns {boolean} - True si se actualizó exitosamente
 */
export function updateQuantity(id, newQty, maxStock = Infinity) {
  if (newQty < 1) return false;
  if (newQty > maxStock) return false;

  cart.update((items) => {
    return items.map((p) =>
      p.id === id ? { ...p, qty: newQty } : p
    );
  });

  return true;
}

export function clearCart() {
  cart.set([]);
}