document.addEventListener('DOMContentLoaded', async () => {
    const cartLink = document.getElementById('cart-link');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    // Helper to update cart counter visually
    function updateCartCounter(count = 0) {
        if (cartLink) {
            cartLink.textContent = `🛒 Cart (${count})`;
        }
    }

    // Fetch initial cart count from backend
    try {
        const res = await fetch('/cart_count');
        const data = await res.json();
        const cartCount = data.count || 0;
        localStorage.setItem('cartCount', cartCount);
        updateCartCounter(cartCount);
    } catch (err) {
        console.error("Failed to fetch cart count:", err);
        updateCartCounter(0);
    }

    // -----------------------------
    // ADD TO CART
    // -----------------------------
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = parseInt(btn.getAttribute('data-id'));
            try {
                const res = await fetch('/add_to_cart', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ id })
                });
                const data = await res.json();

                // Update localStorage + counter
                const cartCount = data.cartCount || 0;
                localStorage.setItem('cartCount', cartCount);
                updateCartCounter(cartCount);

                // Show message
                const msg = document.getElementById('cart-message');
                if (msg) {
                    msg.textContent = data.message || "Added to cart successfully!";
                    msg.classList.remove('d-none');
                    setTimeout(() => msg.classList.add('d-none'), 2000);
                }
            } catch (err) {
                console.error(err);
            }
        });
    });

    // -----------------------------
    // INCREASE / DECREASE QUANTITY
    // -----------------------------
    document.querySelectorAll('.increase-btn, .decrease-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.getAttribute('data-id');
            const action = btn.classList.contains('increase-btn') ? 'increase' : 'decrease';

            try {
                const res = await fetch('/update_cart', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ id, action })
                });
                const data = await res.json();

                if (data.success) {
                    const qtyElement = document.getElementById(`qty-${id}`);
                    qtyElement.textContent = data.qty;

                    // Update totals
                    document.getElementById('total-price').textContent = data.total.toFixed(2);
                    document.getElementById('total-items').textContent = data.total_qty;

                    // Update navbar counter
                    updateCartCounter(data.total_qty);
                }
            } catch (err) {
                console.error(err);
            }
        });
    });

    // -----------------------------
    // REMOVE ITEM
    // -----------------------------
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.getAttribute('data-id');
            try {
                const res = await fetch('/remove_item', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ id })
                });
                const data = await res.json();

                if (data.success) {
                    btn.closest('.card').remove();
                    document.getElementById('total-price').textContent = data.total.toFixed(2);
                    document.getElementById('total-items').textContent = data.total_qty;

                    // Update navbar counter
                    localStorage.setItem('cartCount', data.total_qty);
                    updateCartCounter(data.total_qty);

                    if (data.total_qty === 0) {
                        document.querySelector('.col-md-8').innerHTML = "<p>Your cart is empty.</p>";
                    }
                }
            } catch (err) {
                console.error(err);
            }
        });
    });

    // -----------------------------
    // CHECKOUT BUTTON
    // -----------------------------
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                const res = await fetch('/checkout', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                });
                const data = await res.json();

                if (data.success) {
                    window.location.href = '/checkout/details';
                } else {
                    alert(data.message || "Your cart is empty.");
                }
            } catch (err) {
                console.error(err);
            }
        });
    }
});
