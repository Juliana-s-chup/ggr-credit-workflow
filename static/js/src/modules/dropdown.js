/**
 * Dropdown Module
 * Gère les menus déroulants
 */

export class Dropdown {
  constructor() {
    this.dropdowns = document.querySelectorAll('[data-toggle="dropdown"]');
    this.init();
  }
  
  init() {
    this.dropdowns.forEach(toggle => {
      const parent = toggle.closest('.nav-item-dropdown');
      
      toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggle(parent, toggle);
      });
    });
    
    // Fermer au clic en dehors
    document.addEventListener('click', () => {
      this.closeAll();
    });
    
    // Fermer sur Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeAll();
      }
    });
  }
  
  toggle(parent, toggle) {
    const isOpen = parent.classList.contains('is-open');
    
    // Fermer tous les autres
    this.closeAll();
    
    if (!isOpen) {
      parent.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
    }
  }
  
  closeAll() {
    document.querySelectorAll('.nav-item-dropdown.is-open').forEach(dropdown => {
      dropdown.classList.remove('is-open');
      const toggle = dropdown.querySelector('[data-toggle="dropdown"]');
      if (toggle) {
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }
}
