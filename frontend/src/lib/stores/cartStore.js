import { writable, derived } from 'svelte/store';

/**
 * @typedef {{
 *  id: number | string,
 *  name: string,
 *  price: number,
 *  base_price?: number,
 *  image?: string,
 *  image_url?: string,
 *  main_image?: string,
 *  description?: string,
 *  stock?: number,
 *  variant_sku?: string,
 *  variant_info?: string,
 *  selected_variant?: object
 * }} Product
 */

/**
 * @typedef {Product & { qty: number, cartId: string }} CartItem
 */

// Generar ID único para items del carrito (producto + variante)
function generateCartId(product) {
  if (product.variant_sku) {
    return `${product.id}_${product.variant_sku}`;
  }
  return String(product.id);
}

/** @type {import('svelte/store').Writable<CartItem[]>} */
export const cart = writable([]);

// Store derivado para el total del carrito
export const cartTotal = derived(cart, ($cart) => {
  return $cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
});

// Store derivado para la cantidad total de items
export const cartCount = derived(cart, ($cart) => {
  return $cart.reduce((sum, item) => sum + item.qty, 0);
});

/**
 * @param {Product} product
 * @param {number} quantity - Cantidad a agregar (por defecto 1)
 * @returns {boolean} - True si se agregó correctamente
 */
export function addToCart(product, quantity = 1) {
  let success = true;
  const cartId = generateCartId(product);

  cart.update((items) => {
    const exists = items.find((p) => p.cartId === cartId);
    const currentQty = exists ? exists.qty : 0;
    const newQty = currentQty + quantity;

    // Obtener stock disponible
    const maxStock = product.selected_variant
      ? product.selected_variant.stock
      : (product.stock || Infinity);

    // Validar stock
    if (maxStock !== undefined && newQty > maxStock) {
      success = false;
      return items;
    }

    // Obtener imagen correcta
    const itemImage = product.selected_variant?.image_url
      || product.main_image
      || product.image_url
      || product.image
      || (product.images && product.images[0]);

    if (exists) {
      return items.map((p) =>
        p.cartId === cartId
          ? { ...p, qty: newQty }
          : p
      );
    }

    return [...items, {
      ...product,
      cartId,
      qty: quantity,
      image: itemImage
    }];
  });

  return success;
}

/**
 * Remover un item del carrito
 * @param {string} cartId - ID único del item (producto_variante)
 */
export function removeFromCart(cartId) {
  cart.update((items) => items.filter((p) => p.cartId !== cartId));
}

/**
 * Remover por ID de producto (compatibilidad)
 * @param {number | string} productId
 */
export function removeProductFromCart(productId) {
  cart.update((items) => items.filter((p) => String(p.id) !== String(productId)));
}

/**
 * Actualiza la cantidad de un producto en el carrito
 * @param {string} cartId - ID único del item
 * @param {number} newQty
 * @returns {boolean} - True si se actualizó correctamente
 */
export function updateQuantity(cartId, newQty) {
  if (newQty < 1) {
    return false;
  }

  let success = true;

  cart.update((items) => {
    const item = items.find((p) => p.cartId === cartId);
    if (!item) {
      success = false;
      return items;
    }

    // Obtener stock máximo
    const maxStock = item.selected_variant
      ? item.selected_variant.stock
      : (item.stock || Infinity);

    if (newQty > maxStock) {
      success = false;
      return items;
    }

    return items.map((p) =>
      p.cartId === cartId ? { ...p, qty: newQty } : p
    );
  });

  return success;
}

/**
 * Incrementa la cantidad de un item
 * @param {string} cartId
 * @returns {boolean}
 */
export function incrementQuantity(cartId) {
  let currentQty = 0;
  cart.subscribe(items => {
    const item = items.find(p => p.cartId === cartId);
    if (item) currentQty = item.qty;
  })();

  return updateQuantity(cartId, currentQty + 1);
}

/**
 * Decrementa la cantidad de un item
 * @param {string} cartId
 * @returns {boolean}
 */
export function decrementQuantity(cartId) {
  let currentQty = 0;
  cart.subscribe(items => {
    const item = items.find(p => p.cartId === cartId);
    if (item) currentQty = item.qty;
  })();

  if (currentQty <= 1) {
    removeFromCart(cartId);
    return true;
  }

  return updateQuantity(cartId, currentQty - 1);
}

/**
 * Limpia el carrito
 */
export function clearCart() {
  cart.set([]);
}

/**
 * Obtiene los items formateados para enviar al backend
 * @returns {Array} Items listos para crear orden
 */
export function getCartItemsForOrder() {
  let items = [];
  cart.subscribe(cartItems => {
    items = cartItems.map(item => ({
      product_id: String(item.id),
      quantity: item.qty,
      variant_sku: item.variant_sku || null
    }));
  })();
  return items;
}
