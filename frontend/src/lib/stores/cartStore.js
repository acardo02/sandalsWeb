import { writable } from 'svelte/store';

/**
 * @typedef {{
 *  id: number,
 *  name: string,
 *  price: number,
 *  image: string,
 *  description?: string
 * }} Product
 */

/**
 * @typedef {Product & { qty: number }} CartItem
 */

/** @type {import('svelte/store').Writable<CartItem[]>} */
export const cart = writable([]);

/**
 * @param {Product} product
 */
export function addToCart(product) {
  cart.update((items) => {
    const exists = items.find((p) => p.id === product.id);

    if (exists) {
      return items.map((p) =>
        p.id === product.id
          ? { ...p, qty: p.qty + 1 }
          : p
      );
    }

    return [...items, { ...product, qty: 1 }];
  });
}

/**
 * @param {number} id
 */
export function removeFromCart(id) {
  cart.update((items) => items.filter((p) => p.id !== id));
}

export function clearCart() {
  cart.set([]);
}
