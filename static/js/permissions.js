document.querySelectorAll('[data-permissions-group]').forEach(group => {
    const selectAll = group.querySelector('[data-select-all-permissions]');
    const permissions = [...group.querySelectorAll('input[name="permissions"]')];

    if (!selectAll || !permissions.length) return;

    const syncSelectAll = () => {
        const checkedCount = permissions.filter(permission => permission.checked).length;
        selectAll.checked = checkedCount === permissions.length;
        selectAll.indeterminate = checkedCount > 0 && checkedCount < permissions.length;
    };

    selectAll.addEventListener('change', () => {
        permissions.forEach(permission => {
            permission.checked = selectAll.checked;
        });
        syncSelectAll();
    });

    permissions.forEach(permission => permission.addEventListener('change', syncSelectAll));
    syncSelectAll();
});
