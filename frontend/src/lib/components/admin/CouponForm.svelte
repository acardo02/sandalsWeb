<script>
  export let coupon = null;
  export let onSubmit;
  export let onCancel;

  // Datos del formulario
  let code = coupon?.code || '';
  let description = coupon?.description || '';
  let discountType = coupon?.discount_type || 'percentage';
  let discountValue = coupon?.discount_value || '';
  let minimumAmount = coupon?.minimum_amount || '';
  let maximumDiscount = coupon?.maximum_discount || '';
  let maxUses = coupon?.max_uses || '';
  let maxUsesPerUser = coupon?.max_uses_per_user || 1;
  let isActive = coupon?.is_active ?? true;

  // Fechas
  let validFrom = formatDateForInput(coupon?.valid_from) || getTodayDateTime();
  let validUntil = formatDateForInput(coupon?.valid_until) || getNextMonthDateTime();

  let loading = false;
  let error = '';

  function formatDateForInput(dateString) {
    if (!dateString) return null;
    try {
      const date = new Date(dateString);
      return date.toISOString().slice(0, 16);
    } catch {
      return null;
    }
  }

  function getTodayDateTime() {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16);
  }

  function getNextMonthDateTime() {
    const date = new Date();
    date.setMonth(date.getMonth() + 1);
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return date.toISOString().slice(0, 16);
  }

  function generateCode() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < 8; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    code = result;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    error = '';

    // Validaciones
    if (!code.trim()) {
      error = 'El codigo es requerido';
      return;
    }
    if (!description.trim()) {
      error = 'La descripcion es requerida';
      return;
    }
    if (!discountValue || parseFloat(discountValue) <= 0) {
      error = 'El valor del descuento debe ser mayor a 0';
      return;
    }
    if (discountType === 'percentage' && parseFloat(discountValue) > 100) {
      error = 'El porcentaje no puede ser mayor a 100';
      return;
    }
    if (!validFrom || !validUntil) {
      error = 'Las fechas son requeridas';
      return;
    }

    loading = true;

    try {
      const couponData = {
        code: code.trim().toUpperCase(),
        description: description.trim(),
        discount_type: discountType,
        discount_value: parseFloat(discountValue),
        minimum_amount: minimumAmount ? parseFloat(minimumAmount) : null,
        maximum_discount: maximumDiscount ? parseFloat(maximumDiscount) : null,
        max_uses: maxUses ? parseInt(maxUses) : null,
        max_uses_per_user: parseInt(maxUsesPerUser) || 1,
        valid_from: new Date(validFrom).toISOString(),
        valid_until: new Date(validUntil).toISOString(),
        is_active: isActive,
        applicable_categories: [],
        excluded_products: []
      };

      console.log('Enviando cupon:', couponData);

      const result = await onSubmit(coupon?.code || null, couponData);

      if (result?.success) {
        code = '';
        description = '';
        discountValue = '';
        minimumAmount = '';
        maximumDiscount = '';
        maxUses = '';
      } else {
        error = result?.error || 'Error al guardar el cupon';
      }
    } catch (err) {
      console.error('Error:', err);
      error = err.message || 'Error de conexion';
    } finally {
      loading = false;
    }
  }
</script>

<div class="coupon-form">
  <h2>{coupon ? 'Editar Cupon' : 'Crear Nuevo Cupon'}</h2>

  {#if error}
    <div class="error-message">{error}</div>
  {/if}

  <form on:submit={handleSubmit}>
    <!-- Codigo -->
    <div class="form-group">
      <label for="code">Codigo del Cupon *</label>
      <div class="input-with-button">
        <input
          type="text"
          id="code"
          bind:value={code}
          placeholder="DESCUENTO20"
          disabled={loading || coupon}
          style="text-transform: uppercase"
        />
        {#if !coupon}
          <button type="button" class="btn-secondary" on:click={generateCode} disabled={loading}>
            Generar
          </button>
        {/if}
      </div>
    </div>

    <!-- Descripcion -->
    <div class="form-group">
      <label for="description">Descripcion *</label>
      <input
        type="text"
        id="description"
        bind:value={description}
        placeholder="20% de descuento en toda la tienda"
        disabled={loading}
      />
    </div>

    <!-- Tipo y Valor -->
    <div class="form-row two-cols">
      <div class="form-group">
        <label for="discountType">Tipo de Descuento *</label>
        <select id="discountType" bind:value={discountType} disabled={loading}>
          <option value="percentage">Porcentaje (%)</option>
          <option value="fixed">Monto Fijo ($)</option>
        </select>
      </div>
      <div class="form-group">
        <label for="discountValue">
          Valor * {discountType === 'percentage' ? '(%)' : '($)'}
        </label>
        <input
          type="number"
          id="discountValue"
          step="0.01"
          min="0.01"
          max={discountType === 'percentage' ? 100 : 99999}
          bind:value={discountValue}
          placeholder={discountType === 'percentage' ? '20' : '10.00'}
          disabled={loading}
        />
      </div>
    </div>

    <!-- Limites monetarios -->
    <div class="form-row two-cols">
      <div class="form-group">
        <label for="minimumAmount">Compra Minima ($)</label>
        <input
          type="number"
          id="minimumAmount"
          step="0.01"
          min="0"
          bind:value={minimumAmount}
          placeholder="Sin minimo"
          disabled={loading}
        />
      </div>
      <div class="form-group">
        <label for="maximumDiscount">Descuento Maximo ($)</label>
        <input
          type="number"
          id="maximumDiscount"
          step="0.01"
          min="0"
          bind:value={maximumDiscount}
          placeholder="Sin limite"
          disabled={loading}
        />
        <small>Solo aplica para descuentos porcentuales</small>
      </div>
    </div>

    <!-- Limites de uso -->
    <div class="form-row two-cols">
      <div class="form-group">
        <label for="maxUses">Usos Totales</label>
        <input
          type="number"
          id="maxUses"
          min="1"
          bind:value={maxUses}
          placeholder="Ilimitado"
          disabled={loading}
        />
      </div>
      <div class="form-group">
        <label for="maxUsesPerUser">Usos por Cliente</label>
        <input
          type="number"
          id="maxUsesPerUser"
          min="1"
          bind:value={maxUsesPerUser}
          disabled={loading}
        />
      </div>
    </div>

    <!-- Fechas -->
    <div class="form-row two-cols">
      <div class="form-group">
        <label for="validFrom">Valido Desde *</label>
        <input
          type="datetime-local"
          id="validFrom"
          bind:value={validFrom}
          disabled={loading}
        />
      </div>
      <div class="form-group">
        <label for="validUntil">Valido Hasta *</label>
        <input
          type="datetime-local"
          id="validUntil"
          bind:value={validUntil}
          disabled={loading}
        />
      </div>
    </div>

    <!-- Estado -->
    <div class="form-group checkbox-group">
      <label class="checkbox-label">
        <input type="checkbox" bind:checked={isActive} disabled={loading} />
        <span>Cupon Activo</span>
      </label>
    </div>

    <!-- Botones -->
    <div class="form-actions">
      <button type="button" class="btn-cancel" on:click={onCancel} disabled={loading}>
        Cancelar
      </button>
      <button type="submit" class="btn-submit" disabled={loading}>
        {loading ? 'Guardando...' : coupon ? 'Actualizar Cupon' : 'Crear Cupon'}
      </button>
    </div>
  </form>
</div>

<style>
.coupon-form {
  max-width: 600px;
}

h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-left: 4px solid #c62828;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  font-size: 1rem;
  font-family: inherit;
  background: white;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #000;
}

.form-group input:disabled,
.form-group select:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.form-group small {
  display: block;
  font-size: 0.75rem;
  color: #999;
  margin-top: 0.3rem;
}

.input-with-button {
  display: flex;
  gap: 0.5rem;
}

.input-with-button input {
  flex: 1;
}

.btn-secondary {
  padding: 0.75rem 1rem;
  background: #f0f0f0;
  border: 1px solid #ddd;
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row.two-cols .form-group {
  flex: 1;
}

.checkbox-group {
  padding: 1rem 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.btn-cancel,
.btn-submit {
  padding: 0.9rem 1.8rem;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: #f0f0f0;
  color: #333;
}

.btn-cancel:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-submit {
  background: #000;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: #333;
}

.btn-cancel:disabled,
.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 600px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-cancel,
  .btn-submit {
    width: 100%;
  }
}
</style>
