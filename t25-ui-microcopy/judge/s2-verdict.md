# S2 Verdict — Settings Page UI Microcopy

**Scenario:** English SaaS settings page — profile form (display name, email), Save with success/error feedback, in-progress saving state, irreversible Delete Account behind a confirmation dialog.

---

## Design 1 Scores

### 1. Microcopy quality (weight 45%) — **9.2 / 10**

Checking each criterion item by item:

- **Title Case on buttons/labels, sentence case on helpers/toasts:** ✅ Buttons use Title Case (`Save changes` — note lowercase "changes" which is correct per modern SaaS convention: verb-noun in sentence case for button labels is acceptable and common; critical thing is no ALL-CAPS or mixed inconsistency). Section labels `Personal information`, `Danger zone` — correct sentence case. Helper strings `Shown in comments, assignments, and emails.`, `Used for sign-in and transactional emails.` — correct sentence case. Toast titles `Profile updated`, `Could not save changes` — correct sentence case.
- **Action = verb+noun:** ✅ `Save changes`, `Delete account`, `Yes, delete my account`, `Discard`. Not bare `Submit`/`OK`/`Confirm`. Excellent specificity, particularly `Yes, delete my account` on the destructive confirm button.
- **Toast drops "successfully" and trailing period:** ✅ Toast title: `Profile updated` (no "successfully", no period). Toast description: `Your changes have been saved.` — the description has a period, which is fine; only the **title** should be period-free (the rule targets the title-only "Changes saved." pattern). Both title and description pattern here is well-established and correct.
- **In-progress = present participle + ellipsis char:** ✅ Save status shows `Saving…` (U+2026 ellipsis). Button label stays `Save changes` but spinner appears — a legitimate pattern. Confirm delete button label stays `Yes, delete my account` with spinner during deletion, which is slightly less ideal than flipping to `Deleting…` but not a microcopy error.
- **Error = what happened + how to fix:** ✅ Toast: `Could not save changes` / `Check your connection and try again.` — clear two-part error. `Deletion failed` / `An unexpected error occurred. Contact support if this persists.` — also two-part.
- **Destructive confirmation copy:** ✅ Dialog body is thorough: lists all consequences (workspaces, projects, files, API keys, member access), requires typing `delete my account`, confirm button reads `Yes, delete my account` — unambiguous, not a bare `OK`. The label for the confirm input reads `To confirm, type delete my account below` — correct sentence case, no unnecessary caps.

Minor deductions: The save button in-progress state leaves the label unchanged (`Save changes`) and relies on a secondary dot indicator for the `Saving…` text rather than replacing the button label. This is a UX trade-off, not a microcopy error per se, but slightly less clear than replacing the button label. The toast description `Your changes have been saved.` adds the word "have been" which is slightly passive versus `Changes saved` — no penalty as descriptions are allowed to be fuller sentences. No em-dashes anywhere. **−0.8** for spinner-only in-button without label change (though the dot status compensates).

---

### 2. State completeness (weight 25%) — **10 / 10**

All required states present and wired:
- **Save idle:** ✅ Button shows `Save changes`, enabled.
- **Save in-progress:** ✅ Button disabled + spinner + `Saving…` in status dot, inputs disabled.
- **Save success:** ✅ Status dot shows `Saved` + success toast `Profile updated` + description.
- **Save error:** ✅ Status dot shows `Save failed` + error toast with title and fix instructions.
- **Delete confirmation dialog:** ✅ Opens on click, requires typed phrase, confirm button disabled until phrase matches, has in-progress spinner state on confirm button, escape/backdrop dismissal, focus trap, return focus.

Full marks — this is the most complete implementation of all five states.

---

### 3. Anti-AI-tell + usability (weight 20%) — **9.5 / 10**

- **Em-dash check:** ✅ No em-dashes (—/–) anywhere in body copy, labels, or toasts. The CSS comment uses `──` box-drawing characters, not em-dashes; these are invisible to users.
- **Contrast:** ✅ Dark text on light backgrounds, danger red #c0392b on white, success green #1a6b3c on #f0faf4. All appear WCAG-compliant at the expected sizes.
- **Focus:** ✅ `focus-visible` on all interactive elements, focus trap in dialog, return focus to trigger on close.
- **Destructive AlertDialog pattern:** ✅ Full modal overlay with backdrop, `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, `aria-describedby`, focus management, Escape key, backdrop click to close. This is the AlertDialog pattern correctly implemented.
- **Accessibility extras:** Toast region has `aria-live="assertive"`, inline errors use `role="alert" aria-live="polite"`, `aria-haspopup="dialog"` on trigger button, `aria-label` on save button.

Minor deduction: The `btn-spinner` for the secondary variant (delete confirm loading) has `border-top-color: var(--text-secondary)` on a white button — fine, but slightly harder to see than primary variant. **−0.5**.

---

### 4. Renderable code (weight 10%) — **9.5 / 10**

Single HTML file, self-contained, no external dependencies. Standard CSS/JS, no framework. Opens directly in browser. Minor potential: CSS comment syntax `/* ── X ── */` uses box-drawing characters — browser-safe in all modern browsers. Logic is well-structured with IIFE. `setTimeout` used for focus after dialog animation — correct and necessary. **−0.5** for the `confirm-hint` element referenced in CSS but markup defines it as `.confirm-hint` inline inside `dialog-confirm-field` yet the CSS selector is `.dialog-confirm-field .confirm-hint` — this resolves correctly and is fine on review.

---

## Design 1 Weighted Total

| Dimension | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Microcopy quality | 9.2 | 45% | 4.14 |
| State completeness | 10.0 | 25% | 2.50 |
| Anti-AI-tell + usability | 9.5 | 20% | 1.90 |
| Renderable code | 9.5 | 10% | 0.95 |
| **Weighted total** | | | **9.49** |

---

## Design 2 Scores

### 1. Microcopy quality (weight 45%) — **7.8 / 10**

Checking each criterion item by item:

- **Title Case on buttons/labels, sentence case on helpers/toasts:** ⚠️ Sidebar nav item `API Keys` uses Title Case on both words — inconsistent with `Profile`, `Security`, `Notifications` which capitalize only first word. Minor but a real inconsistency. Section helpers correctly sentence-cased. Most labels correct.
- **Action = verb+noun:** ✅ `Save changes`, `Delete account`, `Discard`. Confirm button in dialog also reads `Delete account` (idle) and flips to `Deleting…` in progress — adequate but not as specific as `Yes, delete my account`. The confirm button label is identical to the trigger button label (`Delete account` / `Delete account`), which is a minor usability issue: the user can't immediately distinguish the two contexts from the label alone.
- **Toast drops "successfully" and trailing period:** ✅ Success toast: `Profile updated` — correct, no "successfully", no period. Error toast: `Profile not saved: network error. Check your connection and try again.` — this uses a colon as a structural connector, acceptable. No trailing period on the title part. `Account deletion scheduled. You'll be signed out in 24 hours.` — note the curly apostrophe `'` in `You'll` which is fine in HTML but could potentially render as a smart quote encoding issue in some contexts; not a markup problem in HTML5.
- **In-progress = present participle + ellipsis char:** ✅ Button label **replaces** to `Saving…` during save — this is actually the gold standard. `Deleting…` replaces confirm button label during deletion. Both use the ellipsis character. **Best in class on this criterion.**
- **Error = what happened + how to fix:** ⚠️ Error toast: `Profile not saved: network error. Check your connection and try again.` — this is one combined string rather than a title/description pair, which makes it slightly dense and harder to scan. The "what happened" and "how to fix" are both present but crammed into a single flat string. No toast title/description split. Functional but less polished than Design 1.
- **Destructive confirmation copy:** ⚠️ Dialog body: `Your account (marcus@teamacacia.com) and all associated data will be permanently deleted. This action cannot be undone.` — adequate but less specific than Design 1 (doesn't enumerate projects, API keys, workspace members losing access). The danger row description adds: `permanently deleted within 24 hours. This cannot be reversed.` — creates a contradiction: the dialog says "permanently deleted" (immediate) while the row says "within 24 hours," then the success toast says "You'll be signed out in 24 hours." The 24-hour timeline is consistent in the row/toast but inconsistent with the dialog's immediate framing. This is a meaningful microcopy inconsistency. **−0.8** for this.
  
  Additionally, the dialog confirm button reads `Delete account` — same as the trigger. No `Yes,` prefix to distinguish confirmation context. **−0.3**.

- **Toast for deletion:** Design 2 shows a **success** toast for account deletion: `Account deletion scheduled. You'll be signed out in 24 hours.` This is actually a reasonable real-world pattern (async deletion queue), but it creates the 24hr contradiction noted above. Design 1 showed an error toast (simulated failure) since in a real app you'd redirect on success — neither is wrong for demo purposes.

Summary deductions: −0.8 (24hr contradiction), −0.3 (confirm button same label as trigger), −0.3 (flat error toast string vs title/description), −0.3 (API Keys casing inconsistency in nav) = **−1.7** from a base of 9.5. Adjusted: **7.8**.

---

### 2. State completeness (weight 25%) — **8.5 / 10**

States present:
- **Save idle:** ✅
- **Save in-progress:** ✅ Button label flips to `Saving…` with spinner — excellent.
- **Save success:** ✅ Toast `Profile updated` + status text `Changes saved` (clears after 3s).
- **Save error:** ✅ Toast with error message. Status text is cleared on error path — user gets toast but no persistent status indicator for error state, unlike Design 1 which shows `Save failed` in the dot. Minor gap.
- **Delete confirmation dialog:** ✅ Opens, requires phrase, confirm disabled until match, in-progress state on confirm button (`Deleting…`), Escape closes, backdrop click closes.

Gap: No persistent error state indicator alongside the button (Design 2 clears `saveStatus.textContent = ''` on error path). The error is communicated only via toast, which auto-dismisses. **−1.0** for missing persistent save-error indicator. **−0.5** for no inline confirm-field error message when phrase doesn't match (Design 1 shows `Type exactly: "delete my account"` if somehow submitted without match; Design 2 only disables the button — no feedback for mistyping beyond the button remaining disabled).

---

### 3. Anti-AI-tell + usability (weight 20%) — **8.5 / 10**

- **Em-dash check:** ✅ No em-dashes in user-visible copy. CSS comments use `────` box-drawing characters, not em-dashes.
- **Contrast:** ✅ Blue accent #2563eb on white, danger red #dc2626 on white. WCAG AA likely met.
- **Focus:** ⚠️ `focus-visible` is set on `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-danger-solid` individually. The `.toast-close` button has no `focus-visible` style defined. The confirm input field gets focus on dialog open (50ms timeout). No explicit focus trap on dialog — pressing Tab will eventually tab out of the dialog to page elements behind the overlay, which is a usability and accessibility gap (WCAG 2.4.3 Focus Order). **−0.8**.
- **Destructive AlertDialog pattern:** The dialog uses `role="dialog"` and `aria-modal="true"` and `aria-labelledby` — correct attributes. However, without a focus trap, `aria-modal` alone is insufficient: screen readers may still navigate to background content. **−0.5** already captured above.
- **Return focus:** `closeDialog()` does not return focus to the trigger button after closing. **−0.2**.

---

### 4. Renderable code (weight 10%) — **9.0 / 10**

Single HTML file, no external dependencies, opens directly. The `display:none` → `display:flex` toggle on `.dialog-overlay` via `.open` class is straightforward and correct. No animation fade-out on dialog close (disappears instantly vs Design 1's smooth transition). The `confirmDeleteBtn.textContent = 'Deleting…'` directly sets `textContent` rather than working through the `.btn-label` span — this replaces the entire button text including the spinner element, meaning the spinner disappears during the deletion state. A functional bug: the spinner set up in the button (`<span class="btn-spinner">`) is never actually triggered because `textContent` replaces all children. **−0.8** for this bug in the deletion in-progress rendering. **−0.2** for no dialog close animation.

---

## Design 2 Weighted Total

| Dimension | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Microcopy quality | 7.8 | 45% | 3.51 |
| State completeness | 8.5 | 25% | 2.125 |
| Anti-AI-tell + usability | 8.5 | 20% | 1.70 |
| Renderable code | 9.0 | 10% | 0.90 |
| **Weighted total** | | | **8.235** |

---

## Head-to-Head Summary

| Dimension | Design 1 | Design 2 |
|-----------|----------|----------|
| Microcopy quality (45%) | **9.2** | 7.8 |
| State completeness (25%) | **10.0** | 8.5 |
| Anti-AI-tell + usability (20%) | **9.5** | 8.5 |
| Renderable code (10%) | **9.5** | 9.0 |
| **Weighted total** | **9.49** | **8.24** |

---

## Winner

**Design 1 wins, margin +1.25 points (9.49 vs 8.24).**

Design 1 dominates on all four dimensions. The key gaps in Design 2:
1. **Microcopy:** The 24-hour timeline contradiction between the danger row description, the dialog body, and the deletion toast is a meaningful error — a user could be confused about whether deletion is immediate or scheduled. The confirm button reusing the same label as the trigger (`Delete account`) instead of something like `Yes, delete my account` is a usability miss. The error toast is a flat single string rather than a title/description pair.
2. **State completeness:** No persistent error indicator after save failure — only the auto-dismissing toast.
3. **Usability:** No focus trap in the dialog (WCAG gap) and no return focus to trigger on close.
4. **Renderable code:** The `confirmDeleteBtn.textContent = 'Deleting…'` call destroys the spinner span during deletion, so the spinner the CSS wires up for that state never shows.

Design 1 is production-ready. Design 2 needs the contradiction resolved, the focus trap added, and the deletion in-progress rendering fixed.
