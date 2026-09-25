import re

html_path = '/home/jignesh/workspace/incipient_work/prepared_modules/incipient_so_approval_discount_customization/static/description/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_walkthrough = """            <!-- Step 1 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 01</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Standard Discount Application</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">Create a Quotation and apply a standard discount within the allowed limits.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_1.png" alt="Standard Discount" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 2 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom flex-lg-row-reverse">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 02</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Quote Sent & Customer Response</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">Once sent to the customer, the quote awaits their decision to either Accept or Reject the offer.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_2.png" alt="Accept or Reject Quote" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 3 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 03</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Ready To Schedule</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">After acceptance, internal confirmation moves the status to Ready To Schedule.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_3.png" alt="Confirm Quote" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 4 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom flex-lg-row-reverse">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 04</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Sales Order Confirmation</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">The standard quote completes its flow by becoming a confirmed Sales Order without requiring extra approvals.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_4.png" alt="Sales Order Confirmed" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 5 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 05</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">High Discount - Send For Approval</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">If a higher discount is applied (e.g., 10%), the system requires the quote to be Sent For Approval.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_5.png" alt="Send For Approval" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 6 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom flex-lg-row-reverse">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 06</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Manager Review</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">The order is locked in the Waiting for Approval stage, where designated managers can Approve or Deny it.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_6.png" alt="Waiting for Approval" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 7 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 07</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Discount Approved</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">Once approved, the record moves to the Approved stage and is ready to be sent to the customer.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_7.png" alt="Approved Stage" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 8 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom flex-lg-row-reverse">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 08</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Send Approved Quote</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">The salesperson can now send the approved high-discount quote to the customer using the Send To Customer button.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_8.png" alt="Send To Customer" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 9 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 09</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Quote Delivered</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">The status updates to Quote Sent, awaiting the customer's final decision on the special offer.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_9.png" alt="Quote Sent" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 10 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom flex-lg-row-reverse">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 10</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Customer Acceptance</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">Upon customer acceptance, the order is marked as Accepted and is ready to be scheduled.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_10.png" alt="Accepted Stage" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 11 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 11</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Final Internal Confirmation</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">Click Confirm to officially lock in the scheduled and accepted order.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_11.png" alt="Confirm Scheduled" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 12 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom flex-lg-row-reverse">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 12</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Sales Order Finalized</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">The transaction safely lands in the Sales Order stage with full audit logs of the approval process.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_12.png" alt="Sales Order Finalized" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 13 -->
            <div class="row align-items-center g-4 mb-5 pb-5 border-bottom">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 13</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Payment Terms Access Control</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">Assign the Payment Terms Readonly permission in User Settings to prevent unauthorized changes to payment structures.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_13.png" alt="User Permissions" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>

            <!-- Step 14 -->
            <div class="row align-items-center g-4 flex-lg-row-reverse">
                <div class="col-lg-5">
                    <span class="px-3 py-1 rounded-pill bg-dark text-white fw-bold small mb-2 d-inline-block">Step 14</span>
                    <h4 class="h3 fw-bold text-dark mb-3" style="font-family: 'Outfit', sans-serif;">Read-Only Enforcement</h4>
                    <p class="text-secondary mb-3" style="line-height: 1.6;">For users without the permission, the Payment Terms field on the Sales Order remains strictly read-only, preventing manual overrides.</p>
                </div>
                <div class="col-lg-7">
                    <div class="p-2 bg-white rounded-4 border shadow-sm">
                        <img src="step_14.png" alt="Read Only Payment Terms" class="img-fluid rounded-3 w-100" onerror="this.onerror=null; this.src='incipient-corp.png';">
                    </div>
                </div>
            </div>
"""

start_marker = "            <!-- Step 1 (Text Left, Image Right) -->"
end_marker = "        </section>" # we will replace up to the end of the walkthrough section, but wait! The end marker is `        </section>\n\n        <!-- EXPANDED 10 FAQ ACCORDION ITEMS -->`

import re
pattern = re.compile(r'            <!-- Step 1 \(Text Left, Image Right\) -->.*?(?=        </section>)', re.DOTALL)
new_content = pattern.sub(new_walkthrough, content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated HTML!")
