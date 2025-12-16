<script>
  export let image;
  export let name;
</script>

<div class="image-section">
  <div class="main-image">
    <img src={image} alt={name} />
  </div>
</div>

<style>
.image-section {
  position: sticky;
  top: 2rem;
  height: fit-content;
}

.main-image {
  position: relative;
  overflow: hidden;
  background: #f5f5f5;
}

.main-image::before {
  content: '';
  display: block;
  padding-bottom: 130%;
}

.main-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1);
  transition: filter 0.6s ease;
}

.main-image:hover img {
  filter: grayscale(0.3);
}

@media (max-width: 968px) {
  .image-section {
    position: relative;
    top: 0;
  }
}
</style>