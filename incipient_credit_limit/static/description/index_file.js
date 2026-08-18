document.addEventListener("DOMContentLoaded", function () {
    // 1. TABS SWITCHING SYSTEM (100% Pure Bootstrap 5 - No custom CSS tags)
    const navLinks = document.querySelectorAll('#myTab .nav-link, .nav .nav-link');
    const tabPanes = document.querySelectorAll('.tab-pane');

    function setActiveTab(clickedLink) {
        navLinks.forEach(l => {
            l.classList.remove('active', 'bg-dark', 'text-white');
            l.classList.add('text-dark', 'bg-transparent');
            l.setAttribute('aria-selected', 'false');
        });
        clickedLink.classList.add('active', 'bg-dark', 'text-white');
        clickedLink.classList.remove('text-dark', 'bg-transparent');
        clickedLink.setAttribute('aria-selected', 'true');

        const targetId = clickedLink.getAttribute('data-bs-target') || clickedLink.getAttribute('data-target') || clickedLink.getAttribute('href');
        if (targetId && targetId.startsWith('#')) {
            tabPanes.forEach(pane => {
                pane.classList.add('d-none');
                pane.classList.remove('show', 'active');
            });
            const targetPane = document.querySelector(targetId);
            if (targetPane) {
                targetPane.classList.remove('d-none');
                targetPane.classList.add('show', 'active');
            }
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            setActiveTab(this);
        });
    });

    // Initialize initial active tab
    const initialActive = document.querySelector('#myTab .nav-link.active') || navLinks[0];
    if (initialActive) {
        setActiveTab(initialActive);
    }

    // 2. FAQ ACCORDION SYSTEM
    const collapseToggles = document.querySelectorAll('[data-bs-toggle="collapse"], [data-toggle="collapse"]');
    collapseToggles.forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetSelector = this.getAttribute('data-bs-target') || this.getAttribute('data-target') || this.getAttribute('href');
            if (!targetSelector) return;
            
            const targetPanel = document.querySelector(targetSelector);
            if (!targetPanel) return;

            const isCollapsed = targetPanel.classList.contains('show');
            const parentSelector = targetPanel.getAttribute('data-bs-parent') || targetPanel.getAttribute('data-parent');
            
            if (parentSelector) {
                const parent = document.querySelector(parentSelector);
                if (parent) {
                    parent.querySelectorAll('.collapse, .accordion-collapse').forEach(panel => {
                        if (panel !== targetPanel) {
                            panel.classList.remove('show');
                            const otherToggle = parent.querySelector(`[data-bs-target="#${panel.id}"], [data-target="#${panel.id}"], [href="#${panel.id}"]`);
                            if (otherToggle) {
                                otherToggle.classList.add('collapsed');
                                otherToggle.setAttribute('aria-expanded', 'false');
                            }
                        }
                    });
                }
            }

            if (isCollapsed) {
                targetPanel.classList.remove('show');
                this.classList.add('collapsed');
                this.setAttribute('aria-expanded', 'false');
            } else {
                targetPanel.classList.add('show');
                this.classList.remove('collapsed');
                this.setAttribute('aria-expanded', 'true');
            }
        });
    });
});
