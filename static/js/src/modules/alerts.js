/**
 * Alerts Module
 * Gère les notifications dismissibles
 */

export class Alerts {
  constructor() {
    this.alerts = document.querySelectorAll('[data-alert]');
    this.init();
  }
  
  init() {
    this.alerts.forEach(alert => {
      const closeBtn = alert.querySelector('[data-dismiss="alert"]');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => this.dismiss(alert));
      }
      
      // Auto-dismiss après 5s pour les success
      if (alert.classList.contains('alert--success')) {
        setTimeout(() => this.dismiss(alert), 5000);
      }
    });
  }
  
  dismiss(alert) {
    alert.style.opacity = '0';
    alert.style.transform = 'translateY(-10px)';
    
    setTimeout(() => {
      alert.remove();
    }, 300);
  }
}
