import { products as productsApi } from '$lib/api'; // Importamos tu api centralizada
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  try {
    // Usamos tu función getAll pasándole los parámetros que creamos en el backend
    const rawProducts = await productsApi.getAll({ 
      limit: 3, 
      random_sample: true 
    });
    
    if (rawProducts) {
      // Mapeamos los datos para asegurar que el frontend no falle
      const products = rawProducts.map((p: any) => ({
        id: p._id || p.id,
        name: p.name,
        // Usamos p.image si existe, si no un placeholder
        image: p.image || '/images/placeholder.jpg', 
        price: p.price
      }));

      return { products };
    }
  } catch (err) {
    console.error("Error cargando productos random:", err);
  }

  return { products: [] };
};