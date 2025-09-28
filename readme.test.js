const fs = require('fs');
const path = require('path');

describe('README.md Content Validation', () => {
  let readmeContent = '';

  beforeAll(() => {
    const readmePath = path.join(__dirname, 'README.md');
    if (fs.existsSync(readmePath)) {
      readmeContent = fs.readFileSync(readmePath, 'utf8');
    }
  });

  describe('FR1: Professional header with name and current role', () => {
    test('should contain name "Nate Swenson"', () => {
      expect(readmeContent).toContain('Nate Swenson');
    });

    test('should contain current role indicators', () => {
      expect(readmeContent).toMatch(/Cloud.*DevOps|DevOps.*Cloud/i);
      expect(readmeContent).toMatch(/AWS Solutions Architect/i);
      expect(readmeContent).toMatch(/Terraform.*Container|Container.*Terraform/i);
    });
  });

  describe('FR2: Technical skills and certifications', () => {
    test('should list AWS and Cloud Computing skills', () => {
      expect(readmeContent).toMatch(/AWS|Amazon Web Services/i);
      expect(readmeContent).toMatch(/Cloud Computing|Cloud/i);
    });

    test('should include specific AWS services', () => {
      expect(readmeContent).toMatch(/EC2/i);
      expect(readmeContent).toMatch(/S3/i);
      expect(readmeContent).toMatch(/Lambda/i);
      expect(readmeContent).toMatch(/EKS/i);
      expect(readmeContent).toMatch(/ECS/i);
      expect(readmeContent).toMatch(/CloudFormation/i);
    });

    test('should mention Infrastructure as Code and Terraform', () => {
      expect(readmeContent).toMatch(/Terraform/i);
      expect(readmeContent).toMatch(/infrastructure.*code|IaC/i);
    });

    test('should include container and Kubernetes technologies', () => {
      expect(readmeContent).toMatch(/Kubernetes/i);
      expect(readmeContent).toMatch(/Docker/i);
      expect(readmeContent).toMatch(/ArgoCD/i);
    });

    test('should mention monitoring tools', () => {
      expect(readmeContent).toMatch(/CloudWatch/i);
      expect(readmeContent).toMatch(/DataDog/i);
    });

    test('should include DevOps practices and tools', () => {
      expect(readmeContent).toMatch(/DevOps/i);
      expect(readmeContent).toMatch(/CI\/CD|Continuous Integration|Continuous Deployment/i);
      expect(readmeContent).toMatch(/automation/i);
    });

    test('should include specific DevOps technologies', () => {
      expect(readmeContent).toMatch(/Datadog/i);
      expect(readmeContent).toMatch(/Terraform/i);
      expect(readmeContent).toMatch(/AWS/i);
      expect(readmeContent).toMatch(/Containers/i);
      expect(readmeContent).toMatch(/EKS/i);
    });

    test('should mention Development expertise', () => {
      expect(readmeContent).toMatch(/Development|Software Engineering/i);
      expect(readmeContent).toMatch(/programming|coding/i);
    });

    test('should include specific Development languages', () => {
      expect(readmeContent).toMatch(/Python/i);
      expect(readmeContent).toMatch(/Javascript/i);
      expect(readmeContent).toMatch(/shell/i);
    });

    test('should include Operations and infrastructure', () => {
      expect(readmeContent).toMatch(/Operations|Infrastructure/i);
      expect(readmeContent).toMatch(/monitoring|observability/i);
      expect(readmeContent).toMatch(/scalability|performance/i);
    });

    test('should mention AI and machine learning', () => {
      expect(readmeContent).toMatch(/AI|Artificial Intelligence/i);
      expect(readmeContent).toMatch(/machine learning|ML/i);
    });

    test('should include Agentic Automation', () => {
      expect(readmeContent).toMatch(/Agentic.*Automation|Automation.*Agentic/i);
      expect(readmeContent).toMatch(/intelligent.*automation|automation.*intelligent/i);
    });

    test('should include specific AI technologies', () => {
      expect(readmeContent).toMatch(/Agentic.*workflows|workflows.*Agentic/i);
      expect(readmeContent).toMatch(/Chatbots/i);
      expect(readmeContent).toMatch(/Claude.*Code|Claude Code/i);
      expect(readmeContent).toMatch(/Cursor/i);
      expect(readmeContent).toMatch(/Bedrock/i);
    });

    test('should mention Test-Driven Development', () => {
      expect(readmeContent).toMatch(/Test-Driven Development|TDD/i);
    });
  });

  describe('FR3: Professional experience', () => {
    test('should mention current role at GoodLeap', () => {
      expect(readmeContent).toContain('GoodLeap');
    });

    test('should describe DevOps and cloud expertise', () => {
      expect(readmeContent).toMatch(/DevOps.*practices|practices.*DevOps/i);
      expect(readmeContent).toMatch(/cloud.*solutions|solutions.*cloud/i);
    });

    test('should indicate collaborative work experience', () => {
      expect(readmeContent).toMatch(/cross-functional.*teams|teams.*cross-functional/i);
    });
  });

  describe('FR4: GitHub statistics and activity metrics', () => {
    test('should include GitHub stats badges or references', () => {
      expect(readmeContent).toMatch(/github.*stats|stats.*github/i);
    });
  });

  describe('FR5: Contact information and social links', () => {
    test('should include LinkedIn profile link', () => {
      expect(readmeContent).toMatch(/linkedin\.com\/in\/natejswenson/);
    });

    test('should include personal website link', () => {
      expect(readmeContent).toMatch(/natejswenson\.github\.io/);
    });
  });

  describe('FR6: Notable achievements and awards', () => {
    test('should mention Arch Forward Award - Hackathon', () => {
      expect(readmeContent).toMatch(/Arch Forward Award.*Hackathon|Hackathon.*Arch Forward Award/i);
    });

    test('should include award date (Nov 2024)', () => {
      expect(readmeContent).toMatch(/Nov.*2024|November.*2024/);
    });

    test('should not include separate certifications section', () => {
      expect(readmeContent).not.toMatch(/##.*Certifications.*Recognition|##.*Certifications.*Awards/i);
    });
  });

  describe('FR7: Section validation', () => {
    test('should not include Languages section', () => {
      expect(readmeContent).not.toMatch(/##.*Languages.*Communication|##.*Languages/i);
    });
  });

  describe('FR8: Personal interests and volunteer work', () => {
    test('should mention GivePower volunteer work', () => {
      expect(readmeContent).toContain('GivePower');
    });

    test('should reference solar power installations', () => {
      expect(readmeContent).toMatch(/solar.*power|solar.*installation/i);
    });

    test('should not mention youth coaching separately', () => {
      expect(readmeContent).not.toMatch(/##.*Youth.*Development|Youth.*Coaching/i);
    });
  });

  describe('FR9: Section management', () => {
    test('should not have a Featured Projects section', () => {
      expect(readmeContent).not.toMatch(/##.*Featured.*Projects|##.*Featured.*Repositories/i);
    });
  });

  describe('FR10: Call-to-action for collaboration', () => {
    test('should include collaboration invitation', () => {
      expect(readmeContent).toMatch(/collaborate|collaboration|connect|contact/i);
    });
  });

  describe('Non-Functional Requirements', () => {
    test('should be valid markdown with proper header structure', () => {
      expect(readmeContent).toMatch(/^#\s+/m); // At least one H1 header
      expect(readmeContent).toMatch(/^##\s+/m); // At least one H2 header
    });

    test('should have reasonable length (not empty)', () => {
      expect(readmeContent.length).toBeGreaterThan(500);
    });

    test('should include proper markdown formatting', () => {
      // Check for lists, links, or other markdown elements
      expect(readmeContent).toMatch(/\[.*\]\(.*\)|\*.*\*|-\s+|1\.\s+/);
    });
  });

  describe('Education and Background', () => {
    test('should mention University of Minnesota-Duluth', () => {
      expect(readmeContent).toMatch(/University of Minnesota.*Duluth|Minnesota.*Duluth/i);
    });

    test('should include education timeframe (2005-2010)', () => {
      expect(readmeContent).toMatch(/2005.*2010|2005-2010/);
    });
  });

  describe('AI and Technology Interests', () => {
    test('should mention AI or machine learning interests', () => {
      expect(readmeContent).toMatch(/AI|Artificial Intelligence|machine learning|ML/i);
    });
  });
});