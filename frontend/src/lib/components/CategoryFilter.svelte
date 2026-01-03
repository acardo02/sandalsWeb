<script>
  export let categories = [];
  export let selectedCategory = 'Todos';
  export let onFilterChange;

  function handleFilterClick(category) {
    selectedCategory = category;
    onFilterChange(category);
  }
</script>

<div class="filter-container">
  <div class="filter-buttons">
    <button 
      class="filter-btn {selectedCategory === 'Todos' ? 'active' : ''}"
      on:click={() => handleFilterClick('Todos')}
    >
      Todos
    </button>
    {#each categories as category}
      <button 
        class="filter-btn {selectedCategory === category ? 'active' : ''}"
        on:click={() => handleFilterClick(category)}
      >
        {category}
      </button>
    {/each}
  </div>
</div>

<style>
.filter-container {
  display: flex;
  justify-content: center;
  margin-bottom: 4rem;
}

.filter-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.filter-btn {
  background: white;
  border: 1px solid #ddd;
  padding: 0.8rem 1.8rem;
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #666;
}

.filter-btn:hover {
  border-color: #000;
  color: #000;
}

.filter-btn.active {
  background: #000;
  color: white;
  border-color: #000;
}

@media (max-width: 768px) {
  .filter-buttons {
    gap: 0.8rem;
  }

  .filter-btn {
    padding: 0.7rem 1.3rem;
    font-size: 0.75rem;
  }
}
</style>