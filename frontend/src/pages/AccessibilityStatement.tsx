import { Helmet } from "react-helmet-async";

export function AccessibilityStatement() {
  return (
    <>
      <Helmet>
        <title>Accessibility Statement - NMTSA Learn</title>
        <meta
          content="Accessibility commitment and features of NMTSA Learn platform"
          name="description"
        />
      </Helmet>

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8">Accessibility Statement</h1>

        <div className="prose prose-lg max-w-none">
          <p className="text-gray-600 mb-6">
            <strong>Last Updated:</strong> October 11, 2025
          </p>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Our Commitment</h2>
            <p className="text-gray-700 mb-4">
              NMTSA Learn is committed to ensuring digital accessibility for
              people with disabilities. We are continually improving the user
              experience for everyone and applying the relevant accessibility
              standards.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Conformance Status</h2>
            <p className="text-gray-700 mb-4">
              The Web Content Accessibility Guidelines (WCAG) define
              requirements for designers and developers to improve accessibility
              for people with disabilities. It defines three levels of
              conformance: Level A, Level AA, and Level AAA.
            </p>
            <p className="text-gray-700 mb-4">
              <strong>
                NMTSA Learn is partially conformant with WCAG 2.1 level AA.
              </strong>{" "}
              Partially conformant means that some parts of the content do not
              fully conform to the accessibility standard.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              Accessibility Features
            </h2>
            <p className="text-gray-700 mb-4">
              Our platform includes the following accessibility features:
            </p>

            <h3 className="text-xl font-semibold mb-3 mt-4">
              Keyboard Navigation
            </h3>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>
                All interactive elements can be accessed using keyboard only
              </li>
              <li>Logical tab order throughout the platform</li>
              <li>Visible focus indicators on all focusable elements</li>
              <li>Skip links to bypass repetitive content</li>
            </ul>

            <h3 className="text-xl font-semibold mb-3 mt-4">
              Screen Reader Support
            </h3>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Semantic HTML structure for proper content hierarchy</li>
              <li>ARIA labels and descriptions where needed</li>
              <li>Alternative text for all meaningful images</li>
              <li>Proper heading structure (H1-H6)</li>
              <li>Form labels and error messages announced correctly</li>
            </ul>

            <h3 className="text-xl font-semibold mb-3 mt-4">Visual Design</h3>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Sufficient color contrast ratios (WCAG AA compliant)</li>
              <li>Text resizing up to 200% without loss of functionality</li>
              <li>No information conveyed by color alone</li>
              <li>Responsive design that works on various screen sizes</li>
              <li>Clear and consistent navigation</li>
            </ul>

            <h3 className="text-xl font-semibold mb-3 mt-4">Video Content</h3>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Captions available for all video content</li>
              <li>Transcripts provided where applicable</li>
              <li>Video player controls are keyboard accessible</li>
              <li>Ability to adjust playback speed</li>
            </ul>

            <h3 className="text-xl font-semibold mb-3 mt-4">
              Forms and Interactive Elements
            </h3>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Clear form labels and instructions</li>
              <li>Error messages that are descriptive and helpful</li>
              <li>Required fields clearly indicated</li>
              <li>Sufficient time to complete forms (no arbitrary timeouts)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              Assistive Technologies
            </h2>
            <p className="text-gray-700 mb-4">
              Our platform is designed to work with the following assistive
              technologies:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Screen readers (JAWS, NVDA, VoiceOver, TalkBack)</li>
              <li>Screen magnification software</li>
              <li>Speech recognition software</li>
              <li>Alternative input devices</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Known Limitations</h2>
            <p className="text-gray-700 mb-4">
              Despite our best efforts, some areas of the platform may have
              accessibility limitations:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>
                Some third-party embedded content may not be fully accessible
              </li>
              <li>
                Older course materials may not meet current accessibility
                standards
              </li>
              <li>
                Some complex interactive elements may have limited accessibility
              </li>
            </ul>
            <p className="text-gray-700 mb-4">
              We are actively working to address these limitations and improve
              accessibility across the platform.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              Browser Compatibility
            </h2>
            <p className="text-gray-700 mb-4">
              For the best accessible experience, we recommend using:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Latest version of Google Chrome</li>
              <li>Latest version of Mozilla Firefox</li>
              <li>Latest version of Microsoft Edge</li>
              <li>Latest version of Safari</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              Mobile Accessibility
            </h2>
            <p className="text-gray-700 mb-4">
              Our platform is designed to be accessible on mobile devices:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Responsive design that adapts to small screens</li>
              <li>Touch targets sized appropriately</li>
              <li>Compatible with iOS VoiceOver and Android TalkBack</li>
              <li>Supports pinch-to-zoom</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Language Support</h2>
            <p className="text-gray-700 mb-4">
              NMTSA Learn is available in English and Spanish. Content is
              properly marked with language attributes for screen readers.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              Feedback and Assistance
            </h2>
            <p className="text-gray-700 mb-4">
              We welcome your feedback on the accessibility of NMTSA Learn. If
              you encounter accessibility barriers, please let us know:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Email: accessibility@nmtsalearn.org</li>
              <li>Phone: (555) 123-4567</li>
              <li>
                Mail: NMTSA Accessibility Team, New Mexico Tribal Safety
                Alliance
              </li>
            </ul>
            <p className="text-gray-700 mb-4">
              We aim to respond to accessibility feedback within 5 business
              days.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Alternative Formats</h2>
            <p className="text-gray-700 mb-4">
              If you need course materials in an alternative format (large
              print, braille, audio), please contact us and we will work to
              accommodate your request.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              Technical Specifications
            </h2>
            <p className="text-gray-700 mb-4">
              Accessibility of NMTSA Learn relies on the following technologies:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>HTML5</li>
              <li>WAI-ARIA</li>
              <li>CSS3</li>
              <li>JavaScript</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              Assessment and Testing
            </h2>
            <p className="text-gray-700 mb-4">
              We regularly test our platform for accessibility using:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Automated accessibility testing tools</li>
              <li>
                Manual testing with screen readers and other assistive
                technologies
              </li>
              <li>Keyboard-only navigation testing</li>
              <li>Testing with users who have disabilities</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Formal Complaints</h2>
            <p className="text-gray-700 mb-4">
              If you are not satisfied with our response to your accessibility
              concerns, you may file a formal complaint. Please include:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Your contact information</li>
              <li>Description of the accessibility barrier</li>
              <li>The page URL where you encountered the issue</li>
              <li>Browser and assistive technology you were using</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              Ongoing Improvements
            </h2>
            <p className="text-gray-700 mb-4">
              We are committed to ongoing accessibility improvements. Our
              roadmap includes:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Regular accessibility audits</li>
              <li>Staff training on accessibility best practices</li>
              <li>Incorporating accessibility into our development process</li>
              <li>Updating older content to meet current standards</li>
              <li>Engaging with the disability community for feedback</li>
            </ul>
          </section>

          <section className="mb-8">
            <p className="text-gray-700">
              This accessibility statement was created on October 11, 2025, and
              will be reviewed and updated annually.
            </p>
          </section>
        </div>
      </div>
    </>
  );
}
