// Neo Brutalist Component Library
class NeoBrutalistLibrary {
  constructor() {
    this.components = {};
    this.initializeComponents();
  }

  // Register all components
  initializeComponents() {
    this.components = {
      Button: {
        template: (props = {}) => `
          <button class="neo-brutalist bg-${props.color || 'yellow-400'} text-${props.textColor || 'black'} text-lg font-bold py-3 px-6 hover:bg-${props.color || 'yellow-400'}-600 transition-none ${props.class || ''}">
            ${props.text || 'Click Me'}
          </button>
        `,
        init: (element, props) => {
          element.innerHTML = this.components.Button.template(props);
          if (props.onClick) {
            element.querySelector('button').addEventListener('click', props.onClick);
          }
        }
      },

      Card: {
        template: (props = {}) => `
          <div class="neo-brutalist bg-white p-6 ${props.class || ''}">
            <h3 class="text-3xl mb-4">${props.title || 'Card Title'}</h3>
            <p class="text-base">${props.content || 'This is a Neo Brutalist card component.'}</p>
          </div>
        `,
        init: (element, props) => {
          element.innerHTML = this.components.Card.template(props);
        }
      },

      Input: {
        template: (props = {}) => `
          <input type="${props.type || 'text'}" 
                 placeholder="${props.placeholder || 'Enter text...'}" 
                 value="${props.value || ''}"
                 class="neo-brutalist w-full p-3 text-lg bg-white border-4 border-black focus:outline-none ${props.class || ''}">
        `,
        init: (element, props) => {
          element.innerHTML = this.components.Input.template(props);
          if (props.onChange) {
            element.querySelector('input').addEventListener('input', props.onChange);
          }
        }
      },

      Toggle: {
        template: (props = {}) => `
          <label class="flex items-center cursor-pointer ${props.class || ''}">
            <input type="checkbox" class="sr-only" ${props.checked ? 'checked' : ''}>
            <div class="neo-brutalist w-12 h-6 bg-gray-300 relative">
              <span class="absolute left-0 top-0 w-6 h-6 bg-black transition-transform duration-200 ease-in-out ${props.checked ? 'translate-x-full' : ''}"></span>
            </div>
            <span class="ml-3 text-lg">${props.label || 'Toggle'}</span>
          </label>
        `,
        init: (element, props) => {
          element.innerHTML = this.components.Toggle.template(props);
          const input = element.querySelector('input');
          const knob = element.querySelector('span');
          input.addEventListener('change', () => {
            knob.style.transform = input.checked ? 'translateX(100%)' : 'translateX(0)';
            if (props.onChange) props.onChange(input.checked);
          });
        }
      },

      Alert: {
        template: (props = {}) => `
          <div class="neo-brutalist bg-${props.type === 'error' ? 'red-500' : 'green-500'} text-white p-4 flex justify-between items-center ${props.class || ''}">
            <span class="text-lg">${props.message || 'This is an alert!'}</span>
            <button class="text-2xl font-bold">×</button>
          </div>
        `,
        init: (element, props) => {
          element.innerHTML = this.components.Alert.template(props);
          const closeBtn = element.querySelector('button');
          closeBtn.addEventListener('click', () => {
            element.remove();
            if (props.onClose) props.onClose();
          });
        }
      },

      Modal: {
        template: (props = {}) => `
          <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center hidden ${props.class || ''}">
            <div class="neo-brutalist bg-white p-8 max-w-md w-full mx-4">
              <h3 class="text-3xl mb-4">${props.title || 'Modal Title'}</h3>
              <p class="text-base mb-6">${props.content || 'This is a Neo Brutalist modal.'}</p>
              <button class="neo-brutalist bg-yellow-400 text-black text-lg font-bold py-2 px-4">Close</button>
            </div>
          </div>
        `,
        init: (element, props) => {
          element.innerHTML = this.components.Modal.template(props);
          const modal = element.querySelector('div');
          const closeBtn = element.querySelector('button');
          closeBtn.addEventListener('click', () => {
            modal.classList.add('hidden');
            if (props.onClose) props.onClose();
          });
          element.open = () => modal.classList.remove('hidden');
          element.close = () => modal.classList.add('hidden');
        }
      },

      Accordion: {
        template: (props = {}) => `
          <div class="neo-brutalist bg-white ${props.class || ''}">
            ${(props.items || [
              { title: 'Section 1', content: 'Content for section 1.' },
              { title: 'Section 2', content: 'Content for section 2.' }
            ]).map((item, index) => `
              <div class="border-b-4 border-black">
                <button class="w-full text-left p-4 text-xl font-bold flex justify-between items-center">
                  ${item.title}
                  <span class="text-2xl">${index === 0 ? '-' : '+'}</span>
                </button>
                <div class="${index === 0 ? '' : 'hidden'} p-4 text-base">
                  ${item.content}
                </div>
              </div>
            `).join('')}
          </div>
        `,
        init: (element, props) => {
          element.innerHTML = this.components.Accordion.template(props);
          const buttons = element.querySelectorAll('button');
          buttons.forEach((button, index) => {
            button.addEventListener('click', () => {
              const content = button.nextElementSibling;
              const isOpen = !content.classList.contains('hidden');
              element.querySelectorAll('div:not(.neo-brutalist)').forEach((div) => div.classList.add('hidden'));
              element.querySelectorAll('button span').forEach((span) => span.textContent = '+');
              if (!isOpen) {
                content.classList.remove('hidden');
                button.querySelector('span').textContent = '-';
              }
              if (props.onToggle) props.onToggle(index, !isOpen);
            });
          });
        }
      },

      Badge: {
        template: (props = {}) => `
          <span class="neo-brutalist inline-block bg-${props.color || 'red-500'} text-${props.textColor || 'white'} text-sm font-bold py-1 px-3 ${props.class || ''}">
            ${props.text || 'New'}
          </span>
        `,
        init: (element, props) => {
          element.innerHTML = this.components.Badge.template(props);
        }
      },

      Dropdown: {
        template: (props = {}) => `
          <div class="relative ${props.class || ''}">
            <button class="neo-brutalist bg-yellow-400 text-black text-lg font-bold py-3 px-6">
              ${props.label || 'Select'}
            </button>
            <ul class="neo-brutalist absolute hidden bg-white w-full min-w-[200px] mt-2 z-10">
              ${(props.options || ['Option 1', 'Option 2', 'Option 3']).map(option => `
                <li><a href="#" class="block p-3 text-lg hover:bg-gray-200">${option}</a></li>
              `).join('')}
            </ul>
          </div>
        `,
        init: (element, props) => {
          element.innerHTML = this.components.Dropdown.template(props);
          const button = element.querySelector('button');
          const menu = element.querySelector('ul');
          const options = element.querySelectorAll('li a');
          
          button.addEventListener('click', () => {
            menu.classList.toggle('hidden');
          });
          
          options.forEach((option, index) => {
            option.addEventListener('click', (e) => {
              e.preventDefault();
              button.textContent = option.textContent;
              menu.classList.add('hidden');
              if (props.onSelect) props.onSelect(option.textContent, index);
            });
          });
          
          document.addEventListener('click', (e) => {
            if (!element.contains(e.target)) {
              menu.classList.add('hidden');
            }
          });
        }
      }
    };
  }

  // Create a component
  create(componentName, container, props = {}) {
    if (!this.components[componentName]) {
      console.error(`Component ${componentName} not found`);
      return null;
    }

    const element = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;

    if (!element) {
      console.error('Container element not found');
      return null;
    }

    this.components[componentName].init(element, props);
    return element;
  }

  // Get available components
  getComponents() {
    return Object.keys(this.components);
  }
}

// Initialize library
window.NeoBrutalist = new NeoBrutalistLibrary();