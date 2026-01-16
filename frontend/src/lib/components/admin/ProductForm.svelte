<script>
  import { upload } from '$lib/api';

  export let product = null;
  export let onSubmit;
  export let onCancel;

  // Datos del formulario
  let name = product?.name || '';
  let description = product?.description || '';
  let price = product?.base_price || '';
  let category = product?.category || 'Sandalias';
  let imageUrl = product?.images?.[0] || product?.main_image || '';

  // Tallas y stock
  let sizeVariants = [];

  // Tallas US disponibles
  const shoeSizes = ['5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12', '12.5', '13'];
  const categories = ['Sandalias', 'Tenis'];

  // Inicializar variantes existentes
  if (product?.variants?.length > 0) {
    sizeVariants = product.variants.map(v => ({
      size: v.size,
      stock: v.stock || 0,
      sku: v.sku
    }));
  }

  // Estados
  let loading = false;
  let uploading = false;
  let error = '';
  let imageFile = null;
  let imagePreview = imageUrl;

  // Funciones de tallas
  function toggleSize(size) {
    const exists = sizeVariants.find(v => v.size === size);
    if (exists) {
      sizeVariants = sizeVariants.filter(v => v.size !== size);
    } else {
      const prefix = name ? name.toUpperCase().replace(/\s+/g, '-').slice(0, 8) : 'PROD';
      sizeVariants = [...sizeVariants, {
        size,
        stock: 0,
        sku: `${prefix}-US${size}`
      }];
    }
  }

  function updateStock(size, value) {
    sizeVariants = sizeVariants.map(v =>
      v.size === size ? { ...v, stock: parseInt(value) || 0 } : v
    );
  }

  // Imagen
  function handleImageSelect(e) {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      imageFile = file;
      imagePreview = URL.createObjectURL(file);
    }
  }

  // Enviar formulario
  async function handleSubmit(e) {
    e.preventDefault();
    error = '';

    // Validar
    if (!name.trim()) {
      error = 'El nombre es requerido';
      return;
    }
    if (!price || parseFloat(price) <= 0) {
      error = 'El precio debe ser mayor a 0';
      return;
    }
    if (sizeVariants.length === 0) {
      error = 'Agrega al menos una talla';
      return;
    }

    const totalStock = sizeVariants.reduce((sum, v) => sum + (v.stock || 0), 0);
    if (totalStock === 0) {
      error = 'Agrega stock a al menos una talla';
      return;
    }

    loading = true;

    try {
      // Subir imagen si hay nueva
      let finalImageUrl = imageUrl;
      if (imageFile) {
        uploading = true;
        console.log('Subiendo imagen...');
        const uploadResult = await upload.image(imageFile);
        finalImageUrl = uploadResult.url;
        console.log('Imagen subida:', finalImageUrl);
        uploading = false;
      }

      // Preparar datos
      const productData = {
        name: name.trim(),
        description: description.trim(),
        base_price: parseFloat(price),
        category,
        has_variants: true,
        variants: sizeVariants.map(v => ({
          sku: v.sku,
          size: v.size,
          stock: v.stock,
          price_adjustment: 0,
          is_available: v.stock > 0
        })),
        images: finalImageUrl ? [finalImageUrl] : [],
        tags: [],
        is_featured: false
      };

      console.log('Enviando producto:', productData);

      // Llamar al callback
      const result = await onSubmit(product?.id || null, productData);

      console.log('Resultado:', result);

      if (result?.success) {
        // Limpiar formulario
        name = '';
        description = '';
        price = '';
        category = 'Sandalias';
        sizeVariants = [];
        imageFile = null;
        imagePreview = '';
        imageUrl = '';
      } else {
        error = result?.error || 'Error al guardar';
      }
    } catch (err) {
      console.error('Error:', err);
      error = err.message || 'Error al guardar producto';
    } finally {
      loading = false;
      uploading = false;
    }
  }
</script>

<div class="form-container">
  <h2>{product ? 'Editar Producto' : 'Nuevo Producto'}</h2>

  {#if error}
    <div class="error-box">{error}</div>
  {/if}

  <form on:submit={handleSubmit}>
    <!-- Nombre y Categoria -->
    <div class="row">
      <div class="field">
        <label>Nombre *</label>
        <input type="text" bind:value={name} placeholder="Nombre del producto" disabled={loading} />
      </div>
      <div class="field">
        <label>Categoria *</label>
        <select bind:value={category} disabled={loading}>
          {#each categories as cat}
            <option value={cat}>{cat}</option>
          {/each}
        </select>
      </div>
      <div class="field">
        <label>Precio ($) *</label>
        <input type="number" step="0.01" min="0.01" bind:value={price} placeholder="0.00" disabled={loading} />
      </div>
    </div>

    <!-- Descripcion -->
    <div class="field">
      <label>Descripcion</label>
      <textarea bind:value={description} rows="3" placeholder="Descripcion del producto..." disabled={loading}></textarea>
    </div>

    <!-- Tallas -->
    <div class="sizes-box">
      <h3>Tallas US y Stock</h3>
      <p class="hint">Haz clic en las tallas para agregarlas</p>

      <div class="sizes-grid">
        {#each shoeSizes as size}
          {@const selected = sizeVariants.find(v => v.size === size)}
          <button
            type="button"
            class="size-btn {selected ? 'active' : ''}"
            on:click={() => toggleSize(size)}
            disabled={loading}
          >
            {size}
          </button>
        {/each}
      </div>

      {#if sizeVariants.length > 0}
        <table class="stock-table">
          <thead>
            <tr>
              <th>Talla</th>
              <th>Stock</th>
              <th>SKU</th>
            </tr>
          </thead>
          <tbody>
            {#each sizeVariants.sort((a, b) => parseFloat(a.size) - parseFloat(b.size)) as v}
              <tr>
                <td><strong>US {v.size}</strong></td>
                <td>
                  <input
                    type="number"
                    min="0"
                    value={v.stock}
                    on:input={(e) => updateStock(v.size, e.target.value)}
                    class="stock-input"
                    disabled={loading}
                  />
                </td>
                <td class="sku">{v.sku}</td>
              </tr>
            {/each}
          </tbody>
        </table>
        <p class="total">Total: {sizeVariants.reduce((s, v) => s + (v.stock || 0), 0)} unidades</p>
      {/if}
    </div>

    <!-- Imagen -->
    <div class="field">
      <label>Imagen</label>
      <input type="file" accept="image/*" on:change={handleImageSelect} disabled={loading || uploading} />
      {#if uploading}
        <p class="uploading">Subiendo imagen...</p>
      {/if}
      {#if imagePreview}
        <img src={imagePreview} alt="Preview" class="preview" />
      {/if}
    </div>

    <!-- Botones -->
    <div class="buttons">
      <button type="button" class="btn-cancel" on:click={onCancel} disabled={loading}>
        Cancelar
      </button>
      <button type="submit" class="btn-save" disabled={loading || uploading}>
        {#if loading}
          Guardando...
        {:else if product}
          Actualizar
        {:else}
          Crear Producto
        {/if}
      </button>
    </div>
  </form>
</div>

<style>
  .form-container {
    max-width: 800px;
  }

  h2 {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
  }

  h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
  }

  .error-box {
    background: #fee;
    color: #c33;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #c33;
  }

  .row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .field {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  input, select, textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    font-size: 1rem;
    font-family: inherit;
  }

  input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: #000;
  }

  input:disabled, select:disabled, textarea:disabled {
    background: #f5f5f5;
  }

  .sizes-box {
    background: #f9f9f9;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #eee;
  }

  .hint {
    color: #666;
    font-size: 0.85rem;
    margin-bottom: 1rem;
  }

  .sizes-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .size-btn {
    width: 50px;
    height: 40px;
    border: 2px solid #ddd;
    background: white;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
  }

  .size-btn:hover {
    border-color: #000;
  }

  .size-btn.active {
    background: #000;
    color: white;
    border-color: #000;
  }

  .stock-table {
    width: 100%;
    background: white;
    border-collapse: collapse;
    margin-top: 1rem;
  }

  .stock-table th, .stock-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }

  .stock-table th {
    background: #f0f0f0;
    font-size: 0.75rem;
    text-transform: uppercase;
  }

  .stock-input {
    width: 80px;
    text-align: center;
    padding: 0.5rem;
  }

  .sku {
    font-family: monospace;
    color: #666;
    font-size: 0.85rem;
  }

  .total {
    text-align: right;
    margin-top: 1rem;
    padding: 0.75rem;
    background: #e8f5e9;
    font-weight: 500;
  }

  .uploading {
    color: #1565c0;
    font-size: 0.9rem;
    margin-top: 0.5rem;
  }

  .preview {
    max-width: 150px;
    margin-top: 1rem;
    border: 1px solid #ddd;
  }

  .buttons {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #ddd;
  }

  .btn-cancel, .btn-save {
    padding: 1rem 2rem;
    font-size: 0.9rem;
    cursor: pointer;
    border: none;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .btn-cancel {
    background: #eee;
    color: #333;
  }

  .btn-save {
    background: #000;
    color: white;
  }

  .btn-save:disabled, .btn-cancel:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @media (max-width: 768px) {
    .row {
      grid-template-columns: 1fr;
    }
  }
</style>
