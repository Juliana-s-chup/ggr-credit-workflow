/**
 * Sidebar Module
 * Gère le comportement collapsible du sidebar
 */

export class Sidebar {
  constructor() {
    this.sidebar = document.querySelector('[data-sidebar]');
    this.toggle = document.querySelector('[data-sidebar-toggle]');
    this.storageKey = 'sidebar-collapsed';
    
    if (this.sidebar && this.toggle) {
      this.init();
    }
  }
  
  init() {
    // Restaurer l'état depuis localStorage
    const isCollapsed = localStorage.getItem(this.storageKey) === 'true';
    if (isCollapsed) {
      this.collapse();
    }
    
    this.toggle.addEventListener('click', () => this.toggleCollapse());
  }
  
  toggleCollapse() {
    this.sidebar.classList.contains('is-collapsed') 
      ? this.expand() 
      : this.collapse();
  }
  
  collapse() {
    this.sidebar.classList.add('is-collapsed');
    this.toggle.setAttribute('aria-label', 'Agrandir le menu');
    localStorage.setItem(this.storageKey, 'true');
  }
  
  expand() {
    this.sidebar.classList.remove('is-collapsed');
    this.toggle.setAttribute('aria-label', 'Réduire le menu');
    localStorage.setItem(this.storageKey, 'false');
  }
}
