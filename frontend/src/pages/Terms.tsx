import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";

export function Terms() {
  const { t } = useTranslation();

  return (
    <>
      <Helmet>
        <title>{t("legal.terms")} - NMTSA Learn</title>
        <meta
          content="Terms of Service for NMTSA Learn platform"
          name="description"
        />
      </Helmet>

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>

        <div className="prose prose-lg max-w-none">
          <p className="text-gray-600 mb-6">
            <strong>Last Updated:</strong> October 11, 2025
          </p>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              1. Acceptance of Terms
            </h2>
            <p className="text-gray-700 mb-4">
              By accessing and using NMTSA Learn (&quot;the Platform&quot;), you
              accept and agree to be bound by the terms and provision of this
              agreement. If you do not agree to abide by the above, please do
              not use this service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">2. Use License</h2>
            <p className="text-gray-700 mb-4">
              Permission is granted to temporarily access the materials
              (information or software) on NMTSA Learn for personal,
              non-commercial transitory viewing only. This is the grant of a
              license, not a transfer of title, and under this license you may
              not:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Modify or copy the materials</li>
              <li>
                Use the materials for any commercial purpose or for any public
                display
              </li>
              <li>
                Attempt to reverse engineer any software contained on the
                Platform
              </li>
              <li>
                Remove any copyright or other proprietary notations from the
                materials
              </li>
              <li>
                Transfer the materials to another person or &quot;mirror&quot;
                the materials on any other server
              </li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">3. User Accounts</h2>
            <p className="text-gray-700 mb-4">
              When you create an account with us, you must provide information
              that is accurate, complete, and current at all times. Failure to
              do so constitutes a breach of the Terms, which may result in
              immediate termination of your account.
            </p>
            <p className="text-gray-700 mb-4">
              You are responsible for safeguarding the password that you use to
              access the Platform and for any activities or actions under your
              password.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              4. Course Enrollment and Access
            </h2>
            <p className="text-gray-700 mb-4">
              When you enroll in a course, you are granted access to the course
              content for the duration specified in the course description.
              Access to courses is provided on an &quot;as is&quot; basis and
              may be subject to periodic updates or modifications.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              5. Intellectual Property
            </h2>
            <p className="text-gray-700 mb-4">
              The Platform and its original content, features, and functionality
              are and will remain the exclusive property of NMTSA and its
              licensors. The Platform is protected by copyright, trademark, and
              other laws of both the United States and foreign countries.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">6. User Content</h2>
            <p className="text-gray-700 mb-4">
              You retain any and all of your rights to any content you submit,
              post, or display on or through the Platform and you are
              responsible for protecting those rights. By posting content, you
              grant us the right and license to use, modify, publicly perform,
              publicly display, reproduce, and distribute such content on and
              through the Platform.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">7. Prohibited Uses</h2>
            <p className="text-gray-700 mb-4">You may not use the Platform:</p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>
                In any way that violates any applicable national or
                international law or regulation
              </li>
              <li>
                To transmit, or procure the sending of, any advertising or
                promotional material, including any &quot;junk mail&quot;,
                &quot;chain letter,&quot; &quot;spam,&quot; or any other similar
                solicitation
              </li>
              <li>
                To impersonate or attempt to impersonate the Company, a Company
                employee, another user, or any other person or entity
              </li>
              <li>
                In any way that infringes upon the rights of others, or in any
                way is illegal, threatening, fraudulent, or harmful
              </li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              8. Certification and Credentials
            </h2>
            <p className="text-gray-700 mb-4">
              Certificates of completion are issued upon successful completion
              of course requirements. These certificates represent completion of
              educational content and should not be construed as professional
              licenses or certifications unless explicitly stated.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              9. Limitation of Liability
            </h2>
            <p className="text-gray-700 mb-4">
              In no event shall NMTSA, nor its directors, employees, partners,
              agents, suppliers, or affiliates, be liable for any indirect,
              incidental, special, consequential or punitive damages, including
              without limitation, loss of profits, data, use, goodwill, or other
              intangible losses, resulting from your access to or use of or
              inability to access or use the Platform.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              10. Changes to Terms
            </h2>
            <p className="text-gray-700 mb-4">
              We reserve the right, at our sole discretion, to modify or replace
              these Terms at any time. If a revision is material, we will
              provide at least 30 days&apos; notice prior to any new terms
              taking effect.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">11. Contact Us</h2>
            <p className="text-gray-700 mb-4">
              If you have any questions about these Terms, please contact us at:
            </p>
            <p className="text-gray-700">
              Email: legal@nmtsalearn.org
              <br />
              Address: New Mexico Tribal Safety Alliance
              <br />
              Phone: (555) 123-4567
            </p>
          </section>
        </div>
      </div>
    </>
  );
}
