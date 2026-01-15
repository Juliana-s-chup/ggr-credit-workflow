/**
 * Navbar Module
 * Gère le comportement du menu responsive
 */

export class Navbar {
  constructor() {
    this.navbar = document.querySelector('[data-toggle="navbar"]');
    this.menu = document.getElementById('navbar-menu');
    this.isOpen = false;
    
    if (this.navbar && this.menu) {
      this.init();
    }
  }
  
  init() {
    this.navbar.addEventListener('click', () => this.toggle());
    
    // Fermer au clic en dehors
    document.addEventListener('click', (e) => {
      if (this.isOpen && !this.navbar.contains(e.target) && !this.menu.contains(e.target)) {
        this.close();
      }
    });
    
    // Fermer sur Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
        this.navbar.focus();
      }
    });
  }
  
  toggle() {
    this.isOpen ? this.close() : this.open();
  }
  
  open() {
    this.isOpen = true;
    this.navbar.setAttribute('aria-expanded', 'true');
    this.menu.classList.add('is-open');
  }
  
  close() {
    this.isOpen = false;
    this.navbar.setAttribute('aria-expanded', 'false');
    this.menu.classList.remove('is-open');
  }
}
