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
                
                // Show notification
                const notification = document.createElement('div');
                notification.className = 'alert alert-success position-fixed top-0 end-0 m-3';
                notification.style.zIndex = '1000';
                notification.textContent = 'Item added to cart!';
                document.body.appendChild(notification);
                
                setTimeout(() => {
                    notification.remove();
                }, 3000);
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