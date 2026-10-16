/* Discourages casual copying only. Public browser content cannot be made download-proof. */
(() => {
 const editing=new URLSearchParams(location.search);
 if(/^\/admin(?:\.html)?\/?$/.test(location.pathname)||(window.parent!==window&&(editing.has('cms_preview')||editing.has('energy_preview'))))return;
 const editable=node=>node?.closest?.('input,textarea,select,[contenteditable="true"],[data-allow-copy],a[href^="mailto:"],a[href^="tel:"]');
 document.addEventListener('contextmenu',event=>{if(event.target.closest?.('img,video')&&!editable(event.target))event.preventDefault();});
 document.addEventListener('dragstart',event=>{if(event.target.closest?.('img,video'))event.preventDefault();});
 document.addEventListener('copy',event=>{const selection=window.getSelection();const node=selection?.anchorNode;const element=node?.nodeType===Node.ELEMENT_NODE?node:node?.parentElement;if(selection?.toString()&&!editable(event.target)&&!editable(element))event.preventDefault();});
})();
