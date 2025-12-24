// Invoice Generator App
class InvoiceApp {
    constructor() {
        this.appEl = document.querySelector('.app');
        this.activeTab = this.appEl?.dataset.activeTab || 'dashboard';
        this.defaultRate = parseFloat(this.appEl?.dataset.defaultRate) || 0;
        this.currency = this.appEl?.dataset.currency || 'EUR';
        this.currentVersion = this.appEl?.dataset.version || '0.1.4';

        this.init();
    }

    init() {
        // Start the clock
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);

        // Check for desktop app updates (not needed for PWA as SW handles it)
        this.checkForDesktopUpdates();

        // Initialize based on active tab
        switch (this.activeTab) {
            case 'dashboard':
                this.initDashboard();
                break;
            case 'invoice':
                this.initInvoiceForm();
                break;
            case 'leaves':
                this.initLeaveCalendar();
                break;
            case 'history':
                this.initHistory();
                break;
            case 'settings':
                this.initSettings();
                break;
        }
    }

    // ==================== Desktop Update Check ====================
    async checkForDesktopUpdates() {
        // Skip if running as PWA with service worker (SW handles updates)
        if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
            return;
        }

        try {
            const response = await fetch('/api/check-update');
            const data = await response.json();

            if (data.success && data.update_available) {
                this.showDesktopUpdateBanner(data.latest_version, data.download_url);
            }
        } catch (error) {
            // Silently fail - update check is not critical
            console.log('Update check skipped:', error.message);
        }
    }

    showDesktopUpdateBanner(newVersion, downloadUrl) {
        const banner = document.getElementById('update-banner');
        const updateBtn = document.getElementById('update-btn');
        const contentSpan = banner?.querySelector('.update-content span');

        if (banner && contentSpan) {
            contentSpan.textContent = `InvoForge v${newVersion} is available!`;

            // For desktop, the update button opens the download page
            if (updateBtn && downloadUrl) {
                updateBtn.textContent = 'Download';
                updateBtn.onclick = () => {
                    window.open(downloadUrl, '_blank');
                };
            }

            banner.classList.remove('hidden');
            if (window.lucide) lucide.createIcons();
        }
    }

    // ==================== Clock ====================
    updateClock() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });

        const currentTimeEl = document.getElementById('current-time');
        if (currentTimeEl) {
            currentTimeEl.textContent = timeStr;
        }

        const dashboardTimeEl = document.getElementById('dashboard-time');
        if (dashboardTimeEl) {
            const dateStr = now.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            dashboardTimeEl.textContent = `${dateStr} • ${timeStr}`;
        }
    }

    // ==================== Dashboard ====================
    async initDashboard() {
        try {
            const response = await fetch('/api/dashboard');
            const data = await response.json();

            if (data.success) {
                // Stats
                document.getElementById('stat-invoices').textContent = data.stats.total_invoices;
                document.getElementById('stat-earned').textContent =
                    `${data.currency} ${this.formatNumber(data.stats.total_earned)}`;
                document.getElementById('stat-leaves').textContent = data.stats.leaves_this_year;

                // Current month
                document.getElementById('month-name').textContent = data.current_month.month_name;
                document.getElementById('month-weekdays').textContent = data.current_month.total_weekdays;
                document.getElementById('month-leaves').textContent = data.current_month.leaves;
                document.getElementById('month-billable').textContent = data.current_month.working_days;

                // Next invoice number
                document.getElementById('next-invoice-num').textContent = data.next_invoice_number;
            }
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        }
    }

    formatNumber(num) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(num);
    }

    // ==================== Invoice Form ====================
    async initInvoiceForm() {
        this.form = document.getElementById('invoice-form');
        this.invoiceNumberInput = document.getElementById('invoice_number');
        this.invoiceDateInput = document.getElementById('invoice_date');
        this.servicePeriodStartInput = document.getElementById('service_period_start');
        this.servicePeriodEndInput = document.getElementById('service_period_end');
        this.workingDaysInput = document.getElementById('total_working_days');
        this.workingDaysHint = document.getElementById('working-days-hint');
        this.leavesInput = document.getElementById('leaves_taken');
        this.leaveDatesContainer = document.getElementById('leave-dates-container');
        this.leaveDatesList = document.getElementById('leave-dates-list');
        this.rateInput = document.getElementById('rate');
        this.downloadSection = document.getElementById('download-section');
        this.generateBtn = document.getElementById('generate-btn');

        // Preview elements
        this.previewBtn = document.getElementById('preview-btn');
        this.previewModal = document.getElementById('document-preview-modal');
        this.previewModalBackdrop = document.querySelector('.preview-modal-backdrop');
        this.documentPreviewContent = document.getElementById('document-preview-content');
        this.previewCloseBtn = document.getElementById('preview-close-btn');
        this.previewPrintBtn = document.getElementById('preview-print-btn');

        this.debounceTimer = null;
        this.currentLeaveDates = [];

        // Set today's date and default service period
        const today = new Date().toISOString().split('T')[0];
        this.invoiceDateInput.value = today;
        this.setDefaultServicePeriod(today);

        // Fetch next invoice number and working days
        await this.fetchNextInvoiceNumber();
        await this.fetchWorkingDaysForServicePeriod();

        this.bindInvoiceEvents();
        this.bindPreviewModal();
        this.updatePreview();
    }

    setDefaultServicePeriod(dateStr) {
        // Set service period to first and last day of the month
        const date = new Date(dateStr + 'T00:00:00'); // Parse as local time
        const year = date.getFullYear();
        const month = date.getMonth();

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);

        // Format as YYYY-MM-DD without timezone conversion
        const formatDate = (d) => {
            const y = d.getFullYear();
            const m = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            return `${y}-${m}-${day}`;
        };

        this.servicePeriodStartInput.value = formatDate(firstDay);
        this.servicePeriodEndInput.value = formatDate(lastDay);
    }

    bindPreviewModal() {
        // Open preview modal
        if (this.previewBtn) {
            this.previewBtn.addEventListener('click', () => this.openPreviewModal());
        }

        // Close on backdrop click
        if (this.previewModalBackdrop) {
            this.previewModalBackdrop.addEventListener('click', () => this.closePreviewModal());
        }

        // Close button
        if (this.previewCloseBtn) {
            this.previewCloseBtn.addEventListener('click', () => this.closePreviewModal());
        }

        // Print button
        if (this.previewPrintBtn) {
            this.previewPrintBtn.addEventListener('click', () => this.printPreview());
        }

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.previewModal?.classList.contains('hidden')) {
                this.closePreviewModal();
            }
        });
    }

    async openPreviewModal() {
        if (!this.previewModal) return;

        // Show modal
        this.previewModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        // Load preview content
        await this.updateDocumentPreview();
    }

    closePreviewModal() {
        if (!this.previewModal) return;

        this.previewModal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    printPreview() {
        window.print();
    }

    async updateDocumentPreview() {
        const data = this.getFormData();

        if (!data.invoice_number || !data.invoice_date) {
            if (this.documentPreviewContent) {
                this.documentPreviewContent.innerHTML = '<p class="preview-placeholder">Please fill in the invoice details first</p>';
            }
            return;
        }

        // Show loading state
        if (this.documentPreviewContent) {
            this.documentPreviewContent.innerHTML = '<p class="preview-placeholder">Loading preview...</p>';
        }

        try {
            const response = await fetch('/api/preview-html', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success && this.documentPreviewContent) {
                this.documentPreviewContent.innerHTML = result.html;
            } else if (this.documentPreviewContent) {
                this.documentPreviewContent.innerHTML = '<p class="preview-placeholder">Failed to generate preview</p>';
            }
        } catch (error) {
            console.error('Document preview error:', error);
            if (this.documentPreviewContent) {
                this.documentPreviewContent.innerHTML = '<p class="preview-placeholder">Error loading preview</p>';
            }
        }
    }

    async fetchNextInvoiceNumber() {
        try {
            const response = await fetch('/api/next-invoice-number');
            const data = await response.json();
            if (data.success) {
                this.invoiceNumberInput.value = data.next_number;
            }
        } catch (error) {
            console.error('Failed to fetch invoice number:', error);
            this.invoiceNumberInput.value = 1;
        }
    }

    async fetchWorkingDaysForServicePeriod() {
        const startDate = this.servicePeriodStartInput?.value;
        const endDate = this.servicePeriodEndInput?.value;

        if (!startDate || !endDate) return;

        try {
            const response = await fetch(`/api/working-days?start_date=${startDate}&end_date=${endDate}`);
            const data = await response.json();

            if (data.success) {
                // Use total_weekdays (gross), not working_days (net)
                // The invoice calculator will subtract leaves_taken
                this.workingDaysInput.value = data.total_weekdays;
                this.leavesInput.value = data.leaves;
                this.workingDaysHint.textContent =
                    `${data.total_weekdays} weekdays - ${data.leaves} leaves = ${data.working_days} billable`;

                // Store leave dates for form submission
                this.currentLeaveDates = data.leave_dates || [];

                // Display leave dates
                if (data.leave_dates && data.leave_dates.length > 0) {
                    this.displayLeaveDates(data.leave_dates);
                } else {
                    this.leaveDatesContainer.classList.add('hidden');
                    this.leaveDatesList.innerHTML = '';
                }
            }
        } catch (error) {
            console.error('Failed to fetch working days:', error);
        }
    }

    displayLeaveDates(dates) {
        this.leaveDatesList.innerHTML = '';

        if (dates.length > 0) {
            this.leaveDatesContainer.classList.remove('hidden');

            dates.forEach(dateStr => {
                const d = new Date(dateStr);
                const formatted = d.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric'
                });

                const item = document.createElement('span');
                item.className = 'leave-date-item';
                item.textContent = formatted;
                this.leaveDatesList.appendChild(item);
            });
        } else {
            this.leaveDatesContainer.classList.add('hidden');
        }
    }

    bindInvoiceEvents() {
        // Invoice date change sets default service period
        this.invoiceDateInput.addEventListener('change', () => {
            this.setDefaultServicePeriod(this.invoiceDateInput.value);
            this.fetchWorkingDaysForServicePeriod();
            this.debouncedPreview();
        });

        // Service period change triggers working days recalculation
        this.servicePeriodStartInput?.addEventListener('change', () => {
            this.fetchWorkingDaysForServicePeriod();
            this.debouncedPreview();
        });
        this.servicePeriodEndInput?.addEventListener('change', () => {
            this.fetchWorkingDaysForServicePeriod();
            this.debouncedPreview();
        });

        // Form fields trigger preview
        const previewFields = ['invoice_number', 'total_working_days', 'leaves_taken', 'rate'];
        previewFields.forEach(field => {
            document.getElementById(field)?.addEventListener('input', () => this.debouncedPreview());
        });

        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    debouncedPreview() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.updatePreview();
            if (this.currentPreviewMode === 'document') {
                this.updateDocumentPreview();
            }
        }, 300);
    }

    async updatePreview() {
        const data = this.getFormData();

        if (!data.invoice_number || !data.invoice_date || !data.total_working_days) {
            return;
        }

        try {
            const response = await fetch('/api/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                document.getElementById('preview-period').textContent = result.preview.service_period;
                document.getElementById('preview-days').textContent = result.preview.days_worked;
                document.getElementById('preview-amount').textContent =
                    `${this.currency} ${result.preview.amount}`;
                document.getElementById('preview-words').textContent = result.preview.amount_in_words;
            }
        } catch (error) {
            console.error('Preview error:', error);
        }
    }

    getFormData() {
        // Use stored leave dates from API (already in ISO format)
        const leaveDates = this.currentLeaveDates || [];

        // Get selected output format
        const formatRadio = document.querySelector('input[name="output_format"]:checked');
        const outputFormat = formatRadio ? formatRadio.value : 'pdf';

        return {
            invoice_number: this.invoiceNumberInput.value,
            invoice_date: this.invoiceDateInput.value,
            service_period_start: this.servicePeriodStartInput?.value,
            service_period_end: this.servicePeriodEndInput?.value,
            validity_year: document.getElementById('validity_year').value,
            total_working_days: this.workingDaysInput.value,
            leaves_taken: this.leavesInput.value || '0',
            leave_dates: leaveDates,
            rate: this.rateInput.value || this.defaultRate,
            output_format: outputFormat
        };
    }

    async handleSubmit(e) {
        e.preventDefault();

        const data = this.getFormData();
        this.setLoading(true);

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.showDownloads(result.files);
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            alert('Failed to generate invoice.');
            console.error('Generate error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    setLoading(isLoading) {
        const btnText = this.generateBtn.querySelector('.btn-text');
        const btnLoader = this.generateBtn.querySelector('.btn-loader');

        if (isLoading) {
            btnText.textContent = 'Generating...';
            btnLoader.classList.remove('hidden');
            this.generateBtn.disabled = true;
        } else {
            btnText.textContent = 'Generate Invoice';
            btnLoader.classList.add('hidden');
            this.generateBtn.disabled = false;
        }
    }

    showDownloads(files) {
        this.downloadSection.classList.remove('hidden');

        const docxLink = document.getElementById('download-docx');
        const pdfLink = document.getElementById('download-pdf');

        // Handle DOCX
        if (files.docx) {
            docxLink.href = `/api/download/${files.docx}`;
            docxLink.classList.remove('hidden');
        } else {
            docxLink.classList.add('hidden');
        }

        // Handle PDF
        if (files.pdf) {
            pdfLink.href = `/api/download/${files.pdf}`;
            pdfLink.classList.remove('hidden', 'disabled');
        } else {
            pdfLink.classList.add('hidden');
        }

        // Show error if PDF failed
        if (files.pdf_error) {
            console.warn('PDF generation issue:', files.pdf_error);
        }

        this.downloadSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // ==================== Leave Calendar ====================
    initLeaveCalendar() {
        const calendarEl = document.getElementById('calendar');
        if (!calendarEl || typeof FullCalendar === 'undefined') return;

        this.modal = document.getElementById('leave-modal');
        this.modalTitle = document.getElementById('modal-title');
        this.modalDate = document.getElementById('modal-date');
        this.modalReason = document.getElementById('modal-reason');
        this.modalDelete = document.getElementById('modal-delete');
        this.modalSave = document.getElementById('modal-save');

        this.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,dayGridWeek'
            },
            events: '/api/leaves/events',
            dateClick: (info) => this.handleDateClick(info),
            eventClick: (info) => this.handleEventClick(info),
            height: 'auto'
        });

        this.calendar.render();
        this.bindModalEvents();
    }

    handleDateClick(info) {
        this.currentLeaveId = null;
        this.modalDate.value = info.dateStr;
        this.modalReason.value = '';
        this.modalTitle.textContent = `Add Leave: ${info.dateStr}`;
        this.modalDelete.classList.add('hidden');
        this.modalSave.textContent = 'Save Leave';
        this.modal.classList.remove('hidden');
    }

    handleEventClick(info) {
        this.currentLeaveId = info.event.id;
        this.modalDate.value = info.event.startStr;
        this.modalReason.value = info.event.extendedProps.reason || '';
        this.modalTitle.textContent = `Leave: ${info.event.startStr}`;
        this.modalDelete.classList.remove('hidden');
        this.modalSave.textContent = 'Update Leave';
        this.modal.classList.remove('hidden');
    }

    bindModalEvents() {
        document.getElementById('modal-cancel').addEventListener('click', () => {
            this.modal.classList.add('hidden');
        });

        this.modalDelete.addEventListener('click', async () => {
            if (this.currentLeaveId) {
                await this.deleteLeave(this.currentLeaveId);
            }
        });

        document.getElementById('leave-modal-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveLeave();
        });

        // Close on backdrop click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.classList.add('hidden');
            }
        });
    }

    async saveLeave() {
        const leaveDate = this.modalDate.value;
        const reason = this.modalReason.value;

        try {
            const response = await fetch('/api/leaves', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ leave_date: leaveDate, reason })
            });

            const result = await response.json();

            if (result.success) {
                this.modal.classList.add('hidden');
                this.calendar.refetchEvents();
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            alert('Failed to save leave.');
            console.error('Save leave error:', error);
        }
    }

    async deleteLeave(leaveId) {
        try {
            const response = await fetch(`/api/leaves/${leaveId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.modal.classList.add('hidden');
                this.calendar.refetchEvents();
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            alert('Failed to delete leave.');
            console.error('Delete leave error:', error);
        }
    }

    // ==================== History ====================
    async initHistory() {
        const listEl = document.getElementById('invoices-list');
        if (!listEl) return;

        try {
            const response = await fetch('/api/invoices');
            const data = await response.json();

            if (data.success && data.invoices.length > 0) {
                listEl.innerHTML = data.invoices.map(inv => `
                    <div class="invoice-item" data-id="${inv.id}">
                        <div class="invoice-info">
                            <span class="invoice-number">#${inv.invoice_number}</span>
                            <span class="invoice-date">${inv.invoice_date}</span>
                            <span class="invoice-period">${inv.service_period}</span>
                            <span class="invoice-amount">${this.currency} ${this.formatNumber(inv.amount)}</span>
                        </div>
                        <div class="invoice-actions">
                            <button type="button" class="action-preview" data-id="${inv.id}" title="Preview Invoice">
                                <i data-lucide="eye"></i>
                            </button>
                            ${inv.docx_filename ? `<a href="/api/download/${inv.docx_filename}" class="action-download" download title="Download DOCX"><i data-lucide="file-text"></i></a>` : ''}
                            ${inv.pdf_filename ? `<a href="/api/download/${inv.pdf_filename}" class="action-download" download title="Download PDF"><i data-lucide="file-type"></i></a>` : ''}
                            <button type="button" class="action-delete" data-id="${inv.id}" data-number="${inv.invoice_number}" title="Delete Invoice">
                                <i data-lucide="trash-2"></i>
                            </button>
                        </div>
                    </div>
                `).join('');

                // Re-initialize lucide icons
                if (window.lucide) {
                    lucide.createIcons();
                }

                // Attach handlers
                this.attachHistoryHandlers();
            } else {
                listEl.innerHTML = '<p class="empty-state">No invoices generated yet. Create your first invoice!</p>';
            }
        } catch (error) {
            listEl.innerHTML = '<p class="empty-state">Failed to load invoices.</p>';
            console.error('Failed to load history:', error);
        }
    }

    attachHistoryHandlers() {
        // Preview handlers
        const previewButtons = document.querySelectorAll('.invoice-item .action-preview');
        previewButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const invoiceId = btn.dataset.id;
                await this.previewStoredInvoice(invoiceId);
            });
        });

        // Delete handlers
        const deleteButtons = document.querySelectorAll('.invoice-item .action-delete');
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const invoiceId = btn.dataset.id;
                const invoiceNumber = btn.dataset.number;

                if (!confirm(`Are you sure you want to delete Invoice #${invoiceNumber}? This will also delete the associated files.`)) {
                    return;
                }

                try {
                    const response = await fetch(`/api/invoices/${invoiceId}`, {
                        method: 'DELETE'
                    });
                    const result = await response.json();

                    if (result.success) {
                        // Remove the item from the list with animation
                        const item = btn.closest('.invoice-item');
                        item.style.opacity = '0';
                        item.style.transform = 'translateX(20px)';
                        setTimeout(() => {
                            item.remove();
                            // Check if list is now empty
                            const listEl = document.getElementById('invoices-list');
                            if (listEl && listEl.children.length === 0) {
                                listEl.innerHTML = '<p class="empty-state">No invoices generated yet. Create your first invoice!</p>';
                            }
                        }, 300);
                    } else {
                        alert('Error: ' + (result.error || 'Failed to delete invoice'));
                    }
                } catch (error) {
                    alert('Failed to delete invoice.');
                    console.error('Delete invoice error:', error);
                }
            });
        });
    }

    async previewStoredInvoice(invoiceId) {
        const modal = document.getElementById('document-preview-modal');
        const content = document.getElementById('document-preview-content');
        const backdrop = document.querySelector('.preview-modal-backdrop');
        const closeBtn = document.getElementById('preview-close-btn');
        const printBtn = document.getElementById('preview-print-btn');

        if (!modal || !content) return;

        // Show modal with loading state
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        content.innerHTML = '<p class="preview-placeholder">Loading preview...</p>';

        // Setup close handlers (if not already bound)
        if (!modal.dataset.bound) {
            backdrop?.addEventListener('click', () => {
                modal.classList.add('hidden');
                document.body.style.overflow = '';
            });
            closeBtn?.addEventListener('click', () => {
                modal.classList.add('hidden');
                document.body.style.overflow = '';
            });
            printBtn?.addEventListener('click', () => window.print());
            modal.dataset.bound = 'true';
        }

        try {
            const response = await fetch(`/api/invoices/${invoiceId}/preview`);
            const result = await response.json();

            if (result.success) {
                content.innerHTML = result.html;
            } else {
                content.innerHTML = '<p class="preview-placeholder">Failed to load preview</p>';
            }
        } catch (error) {
            console.error('Preview error:', error);
            content.innerHTML = '<p class="preview-placeholder">Failed to load preview</p>';
        }
    }

    // ==================== Settings ====================
    async initSettings() {
        const form = document.getElementById('settings-form');
        if (!form) return;

        // Load current settings
        try {
            const response = await fetch('/api/settings');
            const data = await response.json();

            if (data.success) {
                const s = data.settings;
                this.setFieldValue('set_supplier_name', s.supplier_name);
                this.setFieldValue('set_supplier_address', s.supplier_address);
                this.setFieldValue('set_gstin', s.gstin);
                this.setFieldValue('set_pan', s.pan);
                this.setFieldValue('set_supplier_email', s.supplier_email);
                this.setFieldValue('set_client_name', s.client_name);
                this.setFieldValue('set_client_address', s.client_address);
                this.setFieldValue('set_client_country', s.client_country);
                this.setFieldValue('set_client_email', s.client_email);
                this.setFieldValue('set_place_of_supply', s.place_of_supply);
                this.setFieldValue('set_lut_no', s.lut_no);
                this.setFieldValue('set_bank_name', s.bank_name);
                this.setFieldValue('set_account_no', s.account_no);
                this.setFieldValue('set_account_holder', s.account_holder);
                this.setFieldValue('set_swift_code', s.swift_code);
                this.setFieldValue('set_signatory_name', s.signatory_name);
                this.setFieldValue('set_daily_rate', s.daily_rate);
                this.setFieldValue('set_currency', s.currency);
                this.setFieldValue('set_service_description', s.service_description);
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }

        // Handle form submit
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            data.setup_complete = true;

            try {
                const response = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    alert('Settings saved successfully!');
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Failed to save settings.');
                console.error('Save settings error:', error);
            }
        });
    }

    setFieldValue(id, value) {
        const el = document.getElementById(id);
        if (el && value) {
            el.value = value;
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new InvoiceApp();
});
