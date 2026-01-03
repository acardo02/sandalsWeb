<script>
  import { upload } from '$lib/api';

  export let product = null;
  export let onSubmit;
  export let onCancel;

  let name = product?.name || '';
  let description = product?.description || '';
  let price = product?.price || '';
  let stock = product?.stock || '';
  let sku = product?.sku || '';
  let category = product?.category || 'General';
  let image_url = product?.image_url || '';
  
  let uploading = false;
  let loading = false;
  let error = '';
  let imageFile = null;
  let imagePreview = image_url;

  const categories = [
    'General',
    'Ropa',
    'Accesorios',
    'Calzado',
    'Joyería',
    'Hogar',
    'Tecnología'
  ];

  async function handleImageChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      error = 'El archivo debe ser una imagen';
      return;
    }

    imageFile = file;
    imagePreview = URL.createObjectURL(file);
    error = '';
  }

  async function handleSubmit(e) {
    e.preventDefault();
    error = '';
    loading = true;

    try {
      let finalImageUrl = image_url;

      // Si hay imagen nueva, subirla primero
      if (imageFile) {
        uploading = true;
        const uploadResult = await upload.image(imageFile);
        finalImageUrl = uploadResult.url;
        uploading = false;
      }

      const productData = {
        name,
        description: description || '',
        price: parseFloat(price),
        stock: parseInt(stock),
        sku,
        category,
        image_url: finalImageUrl || '',
      };

      const result = await onSubmit(product?.id, productData);

      if (result.success) {
        resetForm();
      } else {
        error = result.error || 'Error al guardar producto';
      }
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
      uploading = false;
    }
  }

  function resetForm() {
    name = '';
    description = '';
    price = '';
    stock = '';
    sku = '';
    category = 'General';
    image_url = '';
    imageFile = null;
    imagePreview = '';
    error = '';
  }

  function handleCancel() {
    resetForm();
    onCancel();
  }
</script>

<div class="product-form">
  <h2>{product ? 'Editar Producto' : 'Nuevo Producto'}</h2>

  <form on:submit={handleSubmit}>
    {#if error}
      <div class="error-message">
        {error}
      </div>
    {/if}

    <div class="form-grid">
      <div class="form-group">
        <label for="name">Nombre del producto *</label>
        <input
          id="name"
          type="text"
          bind:value={name}
          required
          maxlength="150"
          disabled={loading}
        />
      </div>

      <div class="form-group">
        <label for="sku">SKU *</label>
        <input
          id="sku"
          type="text"
          bind:value={sku}
          required
          placeholder="PROD-001"
          disabled={loading}
        />
      </div>

      <div class="form-group">
        <label for="price">Precio ($) *</label>
        <input
          id="price"
          type="number"
          step="0.01"
          min="0"
          bind:value={price}
          required
          disabled={loading}
        />
      </div>

      <div class="form-group">
        <label for="stock">Stock *</label>
        <input
          id="stock"
          type="number"
          min="0"
          bind:value={stock}
          required
          disabled={loading}
        />
      </div>

      <div class="form-group">
        <label for="category">Categoría</label>
        <select id="category" bind:value={category} disabled={loading}>
          {#each categories as cat}
            <option value={cat}>{cat}</option>
          {/each}
        </select>
      </div>
    </div>

    <div class="form-group">
      <label for="description">Descripción</label>
      <textarea
        id="description"
        bind:value={description}
        rows="4"
        disabled={loading}
        placeholder="Descripción detallada del producto..."
      ></textarea>
    </div>

    <div class="form-group">
      <label for="image">Imagen del producto</label>
      <input
        id="image"
        type="file"
        accept="image/*"
        on:change={handleImageChange}
        disabled={loading || uploading}
      />
      
      {#if uploading}
        <p class="upload-status">Subiendo imagen...</p>
      {/if}

      {#if imagePreview}
        <div class="image-preview">
          <img src={imagePreview} alt="Preview" />
        </div>
      {/if}
    </div>

    <div class="form-actions">
      <button type="button" class="btn-secondary" on:click={handleCancel} disabled={loading}>
        Cancelar
      </button>
      <button type="submit" class="btn-primary" disabled={loading || uploading}>
        {loading ? 'Guardando...' : product ? 'Actualizar Producto' : 'Crear Producto'}
      </button>
    </div>
  </form>
</div>

<style>
.product-form {
  max-width: 900px;
}

h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
  margin-bottom: 2rem;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-left: 3px solid #c33;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #333;
}

input,
select,
textarea {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.3s ease;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #000;
}

input:disabled,
select:disabled,
textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

textarea {
  resize: vertical;
}

.upload-status {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #666;
}

.image-preview {
  margin-top: 1rem;
  max-width: 200px;
}

.image-preview img {
  width: 100%;
  height: auto;
  border: 1px solid #ddd;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #ddd;
}

.btn-primary,
.btn-secondary {
  padding: 0.9rem 2rem;
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-primary {
  background: #000;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #333;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>