document.addEventListener('DOMContentLoaded', function() {
    // Add to cart with quantity
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                updateCartCount(result.cart_item_count);
            }
        });
    });
    
    // Update cart count in navbar
    function updateCartCount(count) {
        const cartBadges = document.querySelectorAll('.cart-count');
        cartBadges.forEach(badge => {
            badge.textContent = count;
        });
    }
    
    // Initialize cart count
    fetch('/api/cart/count')
        .then(response => response.json())
        .then(data => updateCartCount(data.count));
});