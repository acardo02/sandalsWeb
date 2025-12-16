<script>
  export let text = "Botón";
  export let onClick = () => {};
</script>

<button on:click={onClick}>
  {text}
</button>

<style>
button {
  background: black;
  color: white;
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
}
button:hover {
  opacity: 0.85;
}
</style>
