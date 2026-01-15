/**
 * Main JS Entry Point
 * GGR Crédit Workflow
 */

import { Navbar } from './src/modules/navbar.js';
import { Sidebar } from './src/modules/sidebar.js';
import { Alerts } from './src/modules/alerts.js';
import { Dropdown } from './src/modules/dropdown.js';

// Init modules when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new Navbar();
  new Sidebar();
  new Alerts();
  new Dropdown();
  
  console.log('✅ GGR Crédit - Front-end initialized');
});
